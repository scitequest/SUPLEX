import logging
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from typing import Any

import ipywidgets as widgets

from suplex.general_constants import BUILD_DATE, RELEASE_STAGE, VERSION_NUMBER
from suplex.ui.styles.color_utils import hex_to_rgba
from suplex.ui.widget_factory import WidgetFactory

logger = logging.getLogger(__name__)


def read_license_text() -> str:
    """
    Return the AGPL license text shipped with the package.

    Installed packages carry the file in their dist-info metadata; a plain checkout
    has it at the repository root.

    Raises:
        FileNotFoundError: If no LICENSE file can be located
    """
    try:
        dist = distribution("suplex")
    except PackageNotFoundError:
        dist = None
    if dist is not None:
        for file in dist.files or []:
            if file.name == "LICENSE":
                return file.read_text()
    checkout_license = Path(__file__).parents[4] / "LICENSE"
    return checkout_license.read_text(encoding="utf-8")


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
            license_title = self.create_section_title("License Agreement", scheme)
            license_text = self.create_license_section(scheme)

            # Version and credits section
            version_html = self.create_version_section(scheme)

            # Main content container
            main_content = WidgetFactory.vbox(
                children=[
                    about_title,
                    about_text,
                    mission_title,
                    mission_text,
                    license_title,
                    license_text,
                    version_html,
                ],
                layout=widgets.Layout(width="100%", height="auto", overflow="auto"),
            )

            logger.debug("About page UI built successfully")
            return main_content

        except Exception as e:
            logger.error("Failed to build about page UI: %s", e, exc_info=True)
            # Return a minimal fallback UI
            return WidgetFactory.html_widget(
                value="<div style='text-align: center; padding: 40px;'>Error loading about page</div>",
                width="100%",
                height="100%",
            )

    def create_section_title(
        self, title: str, scheme: Any, top_margin: str = "20px"
    ) -> widgets.HTML:
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
            emphasis=True,
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
            height="auto",
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
                    SUPLEX is an open-source platform that bridges the gap between measurement and analysis of scientific datasets. It serves as a flexible intermediary between measurement software such as MARTin and modular analysis tools, providing a unified interface for straightforward data ingestion while enabling tailored, variable evaluation through interchangeable modules.
                </p>
                <p style="margin: 0; font-size: {scheme.TEXT.SIZE.DEFAULT};">
                    As practical examples of its capabilities, SUPLEX includes a dedicated MARTin adapter for reliable data import and specialized modules for the analysis of peptide microarrays. The algorithms used in these modules were originally developed by Kreissner for his doctoral thesis, where they were actively applied and rigorously validated in real-world peptide microarray analyses. Provided as battle-tested, ready-to-use components, they offer researchers a reliable and immediately productive starting point. The platform's fully extensible architecture empowers the community to build upon, modify, or replace them with new adapters and analysis modules, ensuring SUPLEX evolves with diverse and emerging scientific needs.
                </p>
            </div>
            """,
            width="100%",
            height="auto",
        )

    def create_license_section(self, scheme: Any) -> widgets.HTML:
        """
        Create the license agreement section content.
        Args:
            scheme: Color scheme for styling
        Returns:
            HTML widget containing the license section
        """
        try:
            license_text = read_license_text()
        except FileNotFoundError:
            license_text = (
                "LICENSE file not found. Please see the repository for license information."
            )

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
                white-space: pre-line;
                text-align: center;
            ">{license_text}</div>
            """,
            width="100%",
            height="auto",
        )

    def create_version_section(self, scheme: Any) -> widgets.HTML:
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
                padding: 15px 20px;
                margin: 20px 20px 0 20px;
                background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT, scheme.OPACITY.MODERATE)};
                border-top: 2px solid {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT, scheme.OPACITY.FULL)};
                border-radius: 0 0 8px 8px;
                font-family: {scheme.TEXT.FONT.DEFAULT};
            ">
                <div style="display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap;">
                    <span style="color: {scheme.TEXT.COLOR.DEFAULT}; font-size: {scheme.TEXT.SIZE.DEFAULT};">
                        <strong>SUPLEX Version:</strong> {VERSION_NUMBER} {RELEASE_STAGE}
                    </span>
                    <div style="width: 2px; height: 30px; background-color: {hex_to_rgba(scheme.LAYOUT_COLOR.INFO_FIELD.DEFAULT, scheme.OPACITY.MODERATE)};"></div>
                    <span style="color: {scheme.TEXT.COLOR.DEFAULT}; font-size: {scheme.TEXT.SIZE.DEFAULT};">
                        <strong>Build Date:</strong> {BUILD_DATE}
                    </span>
                </div>
            </div>
            """,
            width="100%",
            height="auto",
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
