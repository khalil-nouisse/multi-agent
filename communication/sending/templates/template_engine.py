import asyncio
import logging
from typing import Dict, Any, Optional, List
import os
from pathlib import Path
import json
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

from ...shared.models.communication_context import CommunicationContext

logger = logging.getLogger(__name__)

class TemplateEngine:
    """
    Email template engine using Jinja2
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.template_dir = config.get('template_dir', 'templates')
        self.cache_enabled = config.get('cache_enabled', True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True,
            cache_size=100 if self.cache_enabled else 0
        )
        
        # Template cache
        self.template_cache = {}
        
        # Load template metadata
        self.template_metadata = self._load_template_metadata()
        
    def _load_template_metadata(self) -> Dict[str, Any]:
        """
        Load template metadata from JSON file
        """
        try:
            metadata_file = Path(self.template_dir) / 'templates.json'
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning("Could not load template metadata: %s", str(e))
        
        return {}
    
    async def render_template(
        self,
        template_name: str,
        data: Dict[str, Any],
        context: Optional[CommunicationContext] = None
    ) -> Dict[str, Any]:
        """
        Render email template with provided data
        """
        try:
            # Prepare template data
            template_data = data.copy()
            
            # Add context data
            if context:
                template_data.update({
                    'ticket_id': context.ticket_id,
                    'customer_id': context.customer_id,
                    'agent_id': context.agent_id,
                    'context': context.to_dict()
                })
            
            # Add system data
            template_data.update({
                'current_date': asyncio.get_event_loop().time(),
                'system_name': self.config.get('system_name', 'CRM System')
            })
            
            # Load and render HTML template
            html_template = self.env.get_template(f"{template_name}.html")
            html_content = html_template.render(**template_data)
            
            # Try to load and render text template
            text_content = None
            try:
                text_template = self.env.get_template(f"{template_name}.txt")
                text_content = text_template.render(**template_data)
            except TemplateNotFound:
                logger.debug("No text template found for %s", template_name)
            
            return {
                'success': True,
                'html': html_content,
                'text': text_content,
                'template_name': template_name
            }
            
        except TemplateNotFound:
            error_msg = f"Template not found: {template_name}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'template_name': template_name
            }
        except Exception as e:
            error_msg = f"Template rendering error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'template_name': template_name
            }
    
    async def template_exists(self, template_name: str) -> bool:
        """
        Check if template exists
        """
        try:
            self.env.get_template(f"{template_name}.html")
            return True
        except TemplateNotFound:
            return False
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get template metadata information
        """
        return self.template_metadata.get(template_name)
    
    def list_templates(self) -> List[str]:
        """
        List available templates
        """
        try:
            template_files = []
            template_path = Path(self.template_dir)
            
            for file_path in template_path.glob("*.html"):
                template_name = file_path.stem
                template_files.append(template_name)
            
            return sorted(template_files)
            
        except Exception as e:
            logger.error("Error listing templates: %s", str(e))
            return []