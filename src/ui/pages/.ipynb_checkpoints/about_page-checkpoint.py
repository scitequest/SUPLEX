import logging
from typing import Any

import ipywidgets as widgets

from src.ui.widget_factory import WidgetFactory
from src.ui.styles.color_utils import hex_to_rgba
from src.general_constants import VERSION_NUMBER, RELEASE_STAGE, BUILD_DATE

logger = logging.getLogger(__name__)


class AboutPage:
    """
    This page provides users with information about SUPLEX, its mission statement,
    version details, and licensing terms. It's typically shown as the initial
    landing page or accessible through navigation.
    """
    
    def __init__(self) -> None:
        """
        Creates a stateless about page instance that can generate UI content
        dynamically based on the current color scheme.
        """
        logger.debug("Initialized about page object")
    
    def get_ui(self, scheme: Any) -> widgets.Widget:
        """
        Creates a scrollable page with sections for application information,
        mission statement, license agreement, and version details. The page
        is styled according to the provided color scheme.
        
        Args:
            scheme: Color scheme object containing styling information
            
        Returns:
            Widget containing the complete about page interface
        """
        logger.debug("Building about page UI with scheme: %s", scheme.NAME)
        
        try:
            # About section
            about_title = self.create_section_title("About", scheme)
            about_text = self.create_about_section(scheme)
            
            # Mission statement section
            mission_title = self.create_section_title("Our Mission", scheme)
            mission_text = self.create_mission_section(scheme)
            
            # License section
            license_title = self.create_section_title("License Agreement", scheme, top_margin="30px")
            license_text = self.create_license_section(scheme)
            
            # Version and credits section
            credits_html = self.create_credits_section(scheme)
            
            # Main content container
            main_content = WidgetFactory.vbox(
                children=[
                    about_title,
                    about_text,
                    mission_title,
                    mission_text,
                    license_title,
                    license_text,
                    credits_html
                ],
                width="100%",
                height="100%",
                gap="0px",
                align_items="stretch"
            )
              
            # Scrollable container for the entire page
            scrollable_container = WidgetFactory.vbox(
                children=[main_content],
                width="100%",
                height="100%"
            )
            
            # Apply scrolling styling
            scrollable_container.layout.overflow_y = "auto"
            scrollable_container.layout.overflow_x = "hidden"
            scrollable_container.layout.padding = "0px"
            
            logger.debug("About page UI built successfully")
            return scrollable_container
            
        except Exception as e:
            logger.error("Failed to build about page UI: %s", e, exc_info=True)
            # Return a minimal fallback UI
            return WidgetFactory.html_widget(
                value="<div style='text-align: center; padding: 40px;'>Error loading about page</div>",
                width="100%",
                height="100%"
            )
    
    def create_section_title(self, title: str, scheme: Any, top_margin: str = "20px") -> widgets.HTML:
        """
        Create a styled section title.
        
        Args:
            title: The title text to display
            scheme: Color scheme for styling
            top_margin: Top margin for the title (default: "20px")
            
        Returns:
            HTML widget containing the styled title
        """
        return WidgetFactory.label(
            value=f"<h2 style='color: {scheme.TEXT.COLOR.HEADER}; margin: {top_margin} 0 15px 0; text-align: center; font-family: {scheme.TEXT.FONT.HEADER};'>{title}</h2>",
            emphasis=True
        )
    
    def create_about_section(self, scheme: Any) -> widgets.HTML:
        """
        Create the about section content.
        
        Args:
            scheme: Color scheme for styling
            
        Returns:
            HTML widget containing the about section
        """
        return WidgetFactory.html_widget(
            value=f"""
            <div style="
                background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.INFO, scheme.OPACITY.MODERATE)}; 
                border-left: 4px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.INFO, scheme.OPACITY.FULL)}; 
                padding: 20px; 
                margin: 0 20px; 
                border-radius: 0 8px 8px 0;
                line-height: 1.7;
                color: {scheme.TEXT.COLOR.DEFAULT};
                font-family: {scheme.TEXT.FONT.DEFAULT};
                text-align: center;
            ">
                <p style="margin: 0 0 15px 0; font-size: {scheme.TEXT.SIZE.DEFAULT};">
                    The <a href="https://github.com" target="_blank" style="color: {scheme.TEXT.COLOR.HYPERLINK}; text-decoration: none;">SUPLEX</a> platform was developed as a partner software to <a href="https://github.com/scitequest/martin" target="_blank" style="color: {scheme.TEXT.COLOR.HYPERLINK}; text-decoration: none;">MARTin</a> - the MicroArray Rastering Tool.
                </p>
                <p style="margin: 0; font-size: {scheme.TEXT.SIZE.DEFAULT};">
                    Please check out our publication for more information on the <a href="https://doi.org/10.3389/fbinf.2024.1329062" target="_blank" style="color: {scheme.TEXT.COLOR.HYPERLINK}; text-decoration: none;">MARTin Software.</a>
                </p>
            </div>
            """,
            width="100%",
            height="auto"
        )
    
    def create_mission_section(self, scheme: Any) -> widgets.HTML:
        """
        Create the mission statement section content.
        
        Args:
            scheme: Color scheme for styling
            
        Returns:
            HTML widget containing the mission section
        """
        return WidgetFactory.html_widget(
            value=f"""
            <div style="
                background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.INFO, scheme.OPACITY.MODERATE)}; 
                border-left: 4px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.INFO, scheme.OPACITY.FULL)}; 
                padding: 20px; 
                margin: 0 20px; 
                border-radius: 0 8px 8px 0;
                line-height: 1.7;
                color: {scheme.TEXT.COLOR.DEFAULT};
                font-family: {scheme.TEXT.FONT.DEFAULT};
            ">
                <p style="margin: 0 0 15px 0; font-size: {scheme.TEXT.SIZE.DEFAULT};">
                    SUPLEX aims to provide researchers and data scientists with powerful tools for analyzing scientific datasets...
                </p>
                <p style="margin: 0; font-size: {scheme.TEXT.SIZE.DEFAULT};">
                    By working alongside MARTin, we enable comprehensive data analysis workflows...
                </p>
            </div>
            """,
            width="100%",
            height="auto"
        )
    
    def create_license_section(self, scheme: Any) -> widgets.HTML:
        """
        Create the license agreement section content.
        
        Args:
            scheme: Color scheme for styling
            
        Returns:
            HTML widget containing the license section
        """
        license_text = """MIT License
Copyright (c) 2025 Kai Oliver Kreissner & Benjamin Faller

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Additional Terms and Conditions:
1. Data Processing: This software is designed to work with scientific datasets.
   Users are responsible for ensuring they have appropriate permissions to 
   process their data.
2. Research Use: While this software can be used for commercial purposes,
   it is primarily designed for academic and research applications.
3. Third-Party Dependencies: This software may include third-party libraries
   and components, each with their own licensing terms. Users should review
   and comply with all applicable licenses.
4. Data Privacy: Users are responsible for ensuring compliance with applicable
   data protection regulations when processing personal or sensitive data.
5. Support: This software is provided as-is. While we strive to maintain and
   improve the software, support is provided on a best-effort basis.
6. Contributions: Contributions to the project are welcome and should follow
   the project's contribution guidelines available in the repository.
7. Updates: The software may receive updates that could change functionality.
   Users should review changelog information before updating.

For more detailed information about dependencies and their licenses, please
refer to the project documentation and repository files."""
        
        return WidgetFactory.html_widget(
            value=f"""
            <div style="
                background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.INFO, scheme.OPACITY.MODERATE)}; 
                border-left: 4px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.INFO, scheme.OPACITY.FULL)};
                padding: 20px; 
                margin: 0 20px; 
                border-radius: 0 8px 8px 0;
                line-height: 1.7;
                color: {scheme.TEXT.COLOR.DEFAULT};
                font-family: {scheme.TEXT.FONT.DEFAULT};
                font-size: {scheme.TEXT.SIZE.DEFAULT};
                max-height: 400px;
                overflow-y: auto;
                white-space: pre-line;
                text-align: center;
            ">{license_text}</div>
            """,
            width="100%",
            height="auto"
        )
    
    def create_credits_section(self, scheme: Any) -> widgets.HTML:
        """
        Create the version and credits section.
        
        Args:
            scheme: Color scheme for styling
            
        Returns:
            HTML widget containing the credits section
        """
        return WidgetFactory.html_widget(
            value=f"""
            <div style="
                text-align: center; 
                padding: 15px 20px; 
                margin-top: 20px; 
                border-top: 2px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT, scheme.OPACITY.FULL)};
                background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT, scheme.OPACITY.MODERATE)};
                font-family: {scheme.TEXT.FONT.DEFAULT};
            ">
                <div style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;">
                    <span style="color: {scheme.TEXT.COLOR.DEFAULT}; font-size: {scheme.TEXT.SIZE.DEFAULT};">
                        <strong>SUPLEX Version:</strong> {VERSION_NUMBER} {RELEASE_STAGE}
                    </span>
                    <span style="color: {scheme.TEXT.COLOR.DEFAULT}; font-size: {scheme.TEXT.SIZE.DEFAULT};">
                        <strong>Build Date:</strong> {BUILD_DATE}
                    </span>
                </div>
            </div>
            """,
            width="100%",
            height="auto"
        )
    
    def reset(self) -> "AboutPage":
        """
        Reset the about page by returning a new instance.
        
        Since the about page is stateless, this simply returns a new instance.
        
        Returns:
            New AboutPage instance
        """
        logger.debug("About page reset conducted")
        return AboutPage()