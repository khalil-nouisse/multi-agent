from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
import tempfile
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager

# Import your fixed modules
from fixed_database import EcommerceFunctions
from llm_orchestrator import LLMOrchestrator
from audio_processor import AudioProcessor
from audio_response_processor import AudioResponseProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
llm_orchestrator = None
audio_processor = None
audio_response_processor = None
ecom_funcs = None
OPENAI_API_KEY = "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"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    global llm_orchestrator, audio_processor, audio_response_processor, ecom_funcs
    
    # Startup
    logger.info("🚀 Starting E-commerce Bot with Audio Response...")
    
    try:
        if not OPENAI_API_KEY or "YOUR_OPENAI_API_KEY" in OPENAI_API_KEY:
            raise Exception("Valid OpenAI API key is required")
        
        logger.info("🧠 Initializing LLM...")
        llm_orchestrator = LLMOrchestrator(OPENAI_API_KEY)
        
        logger.info("🎤 Loading Whisper...")
        audio_processor = AudioProcessor()
        
        logger.info("🔊 Initializing TTS...")
        audio_response_processor = AudioResponseProcessor()
        
        logger.info("🗄️ Connecting to database...")
        ecom_funcs = EcommerceFunctions()
        
        # Test database
        test_customer = ecom_funcs.get_or_create_customer("+test123")
        logger.info(f"✅ Database test successful: customer {test_customer['id']}")
        
        logger.info("✅ All systems ready with audio response!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="WhatsApp E-commerce Bot with Audio",
    version="4.0.0",
    description="AI e-commerce bot with audio input/output",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class TextRequest(BaseModel):
    message: str
    customer_phone: str
    return_audio: bool = False

@app.post("/process-audio")
async def process_audio(
    audio: UploadFile = File(...),
    customer_phone: str = Form(...),
    return_audio: bool = Form(False)
):
    """Process WhatsApp audio with optional audio response"""
    
    if not customer_phone:
        raise HTTPException(status_code=400, detail="customer_phone required")
    
    try:
        logger.info(f"🎤 Processing audio from {customer_phone} (return_audio: {return_audio})")
        
        # Read and transcribe audio
        audio_bytes = await audio.read()
        logger.info(f"📊 Audio size: {len(audio_bytes)} bytes")
        
        if len(audio_bytes) == 0:
            return {"success": False, "error": "Empty audio file"}
        
        # Transcribe
        logger.info("🔄 Transcribing...")
        transcribed_text = audio_processor.transcribe_audio_bytes(audio_bytes, audio.filename)
        
        if not transcribed_text:
            return {"success": False, "error": "Transcription failed"}
        
        logger.info(f"📝 Transcribed: '{transcribed_text}'")
        
        # Process as text
        response = await process_text_internal(transcribed_text, customer_phone)
        
        result = {
            "success": True,
            "transcribed_text": transcribed_text,
            "response": response["response"],
            "customer_id": response.get("customer_id"),
            "function_called": response.get("function_called")
        }
        
        # Generate audio response if requested
        if return_audio and response["success"]:
            logger.info("🔊 Generating audio response...")
            audio_response = audio_response_processor.generate_audio_response(
                response["response"], 
                OPENAI_API_KEY
            )
            
            if audio_response:
                # Convert to base64 for JSON response
                audio_base64 = audio_response_processor.audio_to_base64(audio_response)
                result["audio_response"] = audio_base64
                result["audio_format"] = "mp3"
                logger.info("✅ Audio response generated")
            else:
                logger.warning("⚠️ Audio response generation failed")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Audio error: {e}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

@app.post("/process-text")
async def process_text_endpoint(request: TextRequest):
    """Process text message with optional audio response"""
    
    response = await process_text_internal(request.message, request.customer_phone)
    
    # Generate audio response if requested
    if request.return_audio and response["success"]:
        logger.info("🔊 Generating audio response...")
        audio_response = audio_response_processor.generate_audio_response(
            response["response"], 
            OPENAI_API_KEY
        )
        
        if audio_response:
            # Convert to base64 for JSON response
            audio_base64 = audio_response_processor.audio_to_base64(audio_response)
            response["audio_response"] = audio_base64
            response["audio_format"] = "mp3"
            logger.info("✅ Audio response generated")
    
    return response

@app.post("/process-text-audio-file")
async def process_text_audio_file(
    message: str = Form(...),
    customer_phone: str = Form(...)
):
    """Process text and return audio response as downloadable file"""
    
    try:
        logger.info(f"💬 Processing text with audio file response: '{message}'")
        
        # Process text
        response = await process_text_internal(message, customer_phone)
        
        if not response["success"]:
            raise HTTPException(status_code=400, detail=response.get("error", "Processing failed"))
        
        # Generate audio response
        logger.info("🔊 Generating audio file...")
        audio_response = audio_response_processor.generate_audio_response(
            response["response"], 
            OPENAI_API_KEY
        )
        
        if not audio_response:
            raise HTTPException(status_code=500, detail="Audio generation failed")
        
        # Save to temp file
        audio_file_path = audio_response_processor.save_audio_to_file(audio_response)
        
        # Return as downloadable file
        return FileResponse(
            audio_file_path,
            media_type="audio/mpeg",
            filename="response.mp3",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
        
    except Exception as e:
        logger.error(f"❌ Audio file error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_text_internal(message: str, customer_phone: str) -> Dict[str, Any]:
    """Internal text processing (same as before)"""
    
    try:
        logger.info(f"💬 Processing: '{message}' from {customer_phone}")
        
        # Get customer
        customer = ecom_funcs.get_or_create_customer(customer_phone)
        customer_id = customer['id']
        logger.info(f"👤 Customer ID: {customer_id}")
        
        # Get history
        conversation_history = ecom_funcs.get_conversation_history(customer_id)
        
        # Process with LLM
        llm_result = llm_orchestrator.process_message(message, customer_id, conversation_history)
        logger.info(f"🧠 LLM result: {llm_result['type']}")
        
        response_text = ""
        
        if llm_result["type"] == "function_call":
            function_name = llm_result["function"]
            function_args = llm_result["arguments"]
            
            logger.info(f"🔧 Calling: {function_name}({function_args})")
            
            try:
                # Execute function
                if function_name == "search_products":
                    result = ecom_funcs.search_products(**function_args)
                    
                elif function_name == "add_to_cart_by_name":
                    result = ecom_funcs.add_to_cart_by_name(customer_id, **function_args)
                    
                elif function_name == "add_to_cart":
                    result = ecom_funcs.add_to_cart(customer_id, **function_args)
                    
                elif function_name == "view_cart":
                    result = ecom_funcs.view_cart(customer_id)
                    
                elif function_name == "remove_from_cart":
                    result = ecom_funcs.remove_from_cart(customer_id, **function_args)
                    
                elif function_name == "confirm_order":
                    result = ecom_funcs.confirm_order(customer_id, **function_args)
                    
                elif function_name == "check_order_status":
                    result = ecom_funcs.check_order_status(customer_id)
                    
                else:
                    result = {"success": False, "message": f"Unknown function: {function_name}"}
                
                logger.info(f"✅ Function executed successfully")
                
                # Generate response
                response_text = llm_orchestrator.generate_function_response(result, message)
                
            except Exception as func_error:
                logger.error(f"❌ Function error: {func_error}")
                response_text = "Sorry, I had trouble processing that request. Please try again."
        
        else:
            # Direct text response
            response_text = llm_result["response"]
        
        # Save conversation
        try:
            ecom_funcs.save_conversation(customer_id, message, response_text)
        except Exception as save_error:
            logger.warning(f"⚠️ Save error: {save_error}")
        
        logger.info(f"💬 Response: '{response_text[:100]}...'")
        
        return {
            "success": True,
            "response": response_text,
            "customer_id": customer_id,
            "function_called": llm_result.get("function"),
            "message_type": llm_result["type"]
        }
        
    except Exception as e:
        logger.error(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "response": "I'm having trouble right now. Please try again! 😊",
            "error": str(e)
        }

# Health check and other endpoints (same as before)
@app.get("/health")
async def health_check():
    """Health check with TTS status"""
    try:
        test_customer = ecom_funcs.get_or_create_customer("+health")
        
        return {
            "status": "healthy",
            "message": "All systems operational with audio support",
            "components": {
                "llm": llm_orchestrator is not None,
                "audio_input": audio_processor is not None,
                "audio_output": audio_response_processor is not None,
                "tts_method": audio_response_processor.tts_method if audio_response_processor else "none",
                "database": ecom_funcs is not None,
                "db_test": test_customer is not None
            },
            "version": "4.0.0"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/products")
async def list_products(limit: int = 10):
    """List products"""
    try:
        products = ecom_funcs.search_products("")
        return {"products": products[:limit], "total": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-tts")
async def test_tts(text: str = Query("Hello! This is a test of the text to speech system.")):
    """Test TTS functionality"""
    try:
        logger.info(f"🧪 Testing TTS with: '{text}'")
        
        audio_response = audio_response_processor.generate_audio_response(text, OPENAI_API_KEY)
        
        if not audio_response:
            return {"success": False, "error": "TTS generation failed", "method": audio_response_processor.tts_method}
        
        # Save to temp file and return
        audio_file_path = audio_response_processor.save_audio_to_file(audio_response, "test_tts.mp3")
        
        return FileResponse(
            audio_file_path,
            media_type="audio/mpeg",
            filename="test_tts.mp3"
        )
        
    except Exception as e:
        logger.error(f"❌ TTS test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting server with audio support...")
    uvicorn.run(app, host="0.0.0.0", port=9002, log_level="info")