import pytest
from unittest.mock import Mock, patch, mock_open
import base64

import ipywidgets as widgets

from suplex.ui.elements.header import Header


class TestHeader:
    """Tests for the Header UI component that displays logo, title, version,
    social media links, and the theme selection dropdown.
    """

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------
    def test_header_initialization(self, mock_gui, mock_schemes):
        """Header initializes with correct references and calls update_ui_element."""
        with patch.object(Header, "update_ui_element") as mock_update:
            header = Header(mock_gui, mock_schemes)

            assert header._gui == mock_gui
            assert header._schemes == mock_schemes
            assert header._selected_scheme == "Default"
            assert header._theme_dropdown is None
            assert header._ui is None
            mock_update.assert_called_once()

    # -------------------------------------------------------------------------
    # Icon loading
    # -------------------------------------------------------------------------
    def test_load_icon_success(self, header):
        """load_icon() converts a PNG file to a base64 data URL img tag."""
        mock_image_data = b"fake_image_data"
        mock_encoded = base64.b64encode(mock_image_data).decode()

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_image_data)):
                result = header.load_icon("/path/to/icon.png", 60)

        assert result == f'<img src="data:image/png;base64,{mock_encoded}" style="height: 60px;">'

    def test_load_icon_jpeg(self, header):
        """load_icon() correctly handles JPEG files (different MIME type)."""
        mock_image_data = b"fake_jpeg_data"
        mock_encoded = base64.b64encode(mock_image_data).decode()

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_image_data)):
                result = header.load_icon("/path/to/icon.jpg", 40)

        assert result == f'<img src="data:image/jpeg;base64,{mock_encoded}" style="height: 40px;">'

    def test_load_icon_file_not_found(self, header):
        """Returns fallback div when the icon file does not exist."""
        with patch("os.path.exists", return_value=False):
            result = header.load_icon("/path/to/missing.png", 60)

        assert '<div style="width: 60px; height: 60px; background: #ddd;' in result

    def test_load_icon_read_error(self, header):
        """Returns fallback div when the file cannot be read."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", side_effect=IOError("Read error")):
                result = header.load_icon("/path/to/icon.png", 60)

        assert '<div style="width: 60px; height: 60px; background: #ddd;' in result

    # -------------------------------------------------------------------------
    # Theme dropdown
    # -------------------------------------------------------------------------
    @patch("suplex.ui.elements.header.widgets")
    def test_update_theme_dropdown(self, mock_widgets, header):
        """update_theme_dropdown() creates a Dropdown with all available schemes."""
        mock_dropdown = Mock()
        mock_widgets.Dropdown.return_value = mock_dropdown

        header.update_theme_dropdown()

        mock_widgets.Dropdown.assert_called_once()
        call_kwargs = mock_widgets.Dropdown.call_args[1]
        assert call_kwargs["options"] == [("Default", "Default"), ("Dark", "Dark")]
        assert call_kwargs["value"] == "Default"
        mock_dropdown.observe.assert_called_once()

    @patch("suplex.ui.elements.header.widgets")
    def test_theme_change_handler(self, mock_widgets, header):
        """Changing the theme updates selected_scheme, rebuilds UI, and notifies GUI."""
        mock_dropdown = Mock()
        mock_dropdown.value = "Dark"
        mock_widgets.Dropdown.return_value = mock_dropdown
        header._theme_dropdown = mock_dropdown
        header.update_ui_element = Mock()

        header.update_theme_dropdown()
        observe_call = mock_dropdown.observe.call_args
        handler = observe_call[0][0]

        header._selected_scheme = "Default"
        mock_dropdown.value = "Dark"
        handler({"new": "Dark"})

        assert header._selected_scheme == "Dark"
        header.update_ui_element.assert_called_once()
        header._gui.update_scheme.assert_called_once_with(header._schemes["Dark"])

    def test_theme_change_same_theme_is_noop(self, header):
        """Selecting the same theme again does nothing (early return)."""
        with patch("suplex.ui.elements.header.widgets") as mock_widgets:
            mock_dropdown = Mock()
            mock_dropdown.value = "Default"
            mock_widgets.Dropdown.return_value = mock_dropdown
            header._theme_dropdown = mock_dropdown
            header.update_ui_element = Mock()

            header.update_theme_dropdown()
            observe_call = mock_dropdown.observe.call_args
            handler = observe_call[0][0]

            header._selected_scheme = "Default"
            mock_dropdown.value = "Default"
            handler({"new": "Default"})

            header.update_ui_element.assert_not_called()
            header._gui.update_scheme.assert_not_called()

    # -------------------------------------------------------------------------
    # UI building
    # -------------------------------------------------------------------------
    @patch("suplex.ui.elements.header.widgets")
    @patch("suplex.ui.elements.header.get_header_styles")
    def test_update_ui_element(self, mock_styles, mock_widgets, header):
        """update_ui_element() assembles the complete header layout with all sections."""
        mock_html = Mock()
        mock_hbox = Mock()
        mock_vbox = Mock()
        mock_widgets.HTML.return_value = mock_html
        mock_widgets.HBox.return_value = mock_hbox
        mock_widgets.VBox.return_value = mock_vbox

        header.load_icon = Mock(side_effect=["<img1>", "<img2>"])
        header.update_theme_dropdown = Mock()
        header._theme_dropdown = Mock()

        header.update_ui_element()

        assert mock_widgets.HTML.call_count >= 3
        assert mock_widgets.HBox.call_count >= 4
        assert mock_widgets.VBox.call_count >= 2
        assert header.load_icon.call_count == 2
        header.update_theme_dropdown.assert_called_once()
        assert header._ui is not None

    @patch("suplex.ui.elements.header.VERSION_NUMBER", "1.0.0")
    @patch("suplex.ui.elements.header.widgets")
    def test_version_display(self, mock_widgets, header):
        """Version number is correctly rendered in the header."""
        mock_html = Mock()
        mock_widgets.HTML.return_value = mock_html

        header.load_icon = Mock(return_value="<img>")
        header.update_theme_dropdown = Mock()
        header._theme_dropdown = Mock()

        header.update_ui_element()

        version_found = any(
            call[1].get("value") and "Version 1.0.0" in call[1]["value"]
            for call in mock_widgets.HTML.call_args_list
        )
        assert version_found

    @patch("suplex.ui.elements.header.widgets")
    def test_social_links_creation(self, mock_widgets, header):
        """Social media links (X, GitHub, MARTin) are present in the generated HTML."""
        mock_html = Mock()
        mock_widgets.HTML.return_value = mock_html

        header.load_icon = Mock(return_value="<img>")
        header.update_theme_dropdown = Mock()
        header._theme_dropdown = Mock()

        header.update_ui_element()

        social_links_found = any(
            call[1].get("value")
            and "https://x.com/scitequest" in call[1]["value"]
            and "https://github.com/scitequest" in call[1]["value"]
            for call in mock_widgets.HTML.call_args_list
        )
        assert social_links_found

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    def test_current_scheme_property(self, header):
        """current_scheme property returns the scheme matching _selected_scheme."""
        header._selected_scheme = "Dark"
        assert header.current_scheme == header._schemes["Dark"]

    def test_ui_property(self, header):
        """ui property returns the built VBox widget."""
        mock_ui = Mock()
        header._ui = mock_ui
        assert header.ui == mock_ui
