from unittest.mock import MagicMock, Mock, patch

import ipywidgets as widgets
import matplotlib.pyplot as plt
import svgutils.transform as sg

from suplex.suplex_modules.submodules.collage import (
    Collage,
    add_padding_to_svgs,
    add_title_to_svg,
    create_collage,
    format_image_to_svg,
    generate_collage_figure,
    get_gridded_svgs,
    get_svg_array_for_svgs,
    scale_svgs,
)
from suplex.suplex_modules.submodules.submodule_constants import (
    COLLAGE_LAYOUT,
    COLOR,
    READING_ORDER,
    SCALE_OPTION,
    TITLE_POSITION,
)


class TestCollageFunctions:
    """Unit tests for the core collage helper functions."""

    # -------------------------------------------------------------------------
    # format_image_to_svg
    # -------------------------------------------------------------------------

    def test_format_image_to_svg_pil(self, mock_pil_image):
        """PIL Image should be converted via matplotlib to SVGFigure."""
        with (
            patch("suplex.suplex_modules.submodules.collage.np.array") as mock_np_array,
            patch("suplex.suplex_modules.submodules.collage.plt") as mock_plt,
            patch("suplex.suplex_modules.submodules.collage.sg.fromfile") as mock_fromfile,
        ):
            # Mock array for PIL path (ndim and shape access)
            mock_arr = MagicMock()
            mock_arr.ndim = 3
            mock_arr.shape = (150, 200, 3)
            mock_np_array.return_value = mock_arr

            mock_svg = Mock()
            mock_fromfile.return_value = mock_svg

            # Critical fix: restore real Figure class so isinstance check passes
            mock_plt.Figure = plt.Figure
            fig_mock = MagicMock(spec=plt.Figure)
            mock_plt.figure.return_value = fig_mock

            result = format_image_to_svg(mock_pil_image, dpi=150)
            assert result == mock_svg
            mock_plt.figure.assert_called_once()

    def test_format_image_to_svg_matplotlib(self, mock_matplotlib_figure):
        """Matplotlib Figure should be saved as SVG and loaded."""
        with (
            patch("suplex.suplex_modules.submodules.collage.sg.fromfile") as mock_fromfile,
            patch("suplex.suplex_modules.submodules.collage.os.remove"),
        ):
            mock_svg = Mock()
            mock_fromfile.return_value = mock_svg
            result = format_image_to_svg(mock_matplotlib_figure)
            assert result == mock_svg
            mock_matplotlib_figure.savefig.assert_called_once()

    def test_format_image_to_svg_already_svg(self, mock_svg_figure):
        """SVGFigure should be returned unchanged."""
        result = format_image_to_svg(mock_svg_figure)
        assert result == mock_svg_figure

    # -------------------------------------------------------------------------
    # SVG manipulation helpers
    # -------------------------------------------------------------------------

    def test_scale_svgs_no_scale(self, mock_collage_svgs):
        """NO_SCALE should return original list unchanged."""
        result = scale_svgs(mock_collage_svgs, SCALE_OPTION.NO_SCALE)
        assert result == mock_collage_svgs

    def test_scale_svgs_downscale_to_width(self, mock_collage_svgs):
        """DOWNSCALE_TO_WIDTH should use smallest width."""
        with patch("suplex.suplex_modules.submodules.collage.sg.SVGFigure") as mock_svg_class:
            mock_new_svg = MagicMock()
            mock_svg_class.return_value = mock_new_svg
            result = scale_svgs(mock_collage_svgs, SCALE_OPTION.DOWNSCALE_TO_WIDTH)
            assert len(result) == len(mock_collage_svgs)
            for svg in result:
                assert svg.set_size.called

    def test_add_padding_to_svgs(self, mock_svg_figure):
        """Padding should increase size and move root element."""
        with patch("suplex.suplex_modules.submodules.collage.sg.SVGFigure") as mock_svg_class:
            mock_new_svg = MagicMock()
            mock_svg_class.return_value = mock_new_svg
            result = add_padding_to_svgs([mock_svg_figure], 10, 20)
            assert len(result) == 1
            assert result[0].set_size.called
            mock_svg_figure.getroot.return_value.moveto.assert_called_once_with(10, 20)

    def test_get_gridded_svgs_equal_all(self, mock_collage_svgs):
        """GRID_EQUAL_ALL should center images with padding."""
        with patch("suplex.suplex_modules.submodules.collage.sg.SVGFigure") as mock_svg_class:
            mock_new_svg = MagicMock()
            mock_svg_class.return_value = mock_new_svg
            result = get_gridded_svgs(mock_collage_svgs, COLLAGE_LAYOUT.GRID_EQUAL_ALL)
            assert len(result) == len(mock_collage_svgs)

    def test_get_svg_array_for_svgs_grid(self, mock_collage_svgs):
        """Should create correct 2D array for grid layout."""
        array = get_svg_array_for_svgs(
            mock_collage_svgs,
            n_cols=2,
            layout=COLLAGE_LAYOUT.GRID_EQUAL_ALL,
            reading_order=READING_ORDER.LEFT_RIGHT_TOP_BOTTOM,
        )
        assert len(array) == 2
        assert len(array[0]) == 2

    # -------------------------------------------------------------------------
    # Higher-level collage creation
    # -------------------------------------------------------------------------

    def test_generate_collage_figure_empty(self):
        """Empty array should return minimal SVG."""
        fig = generate_collage_figure([])
        assert isinstance(fig, sg.SVGFigure)

    def test_add_title_to_svg_top(self, mock_svg_figure):
        """Title at TOP position should add height and text element."""
        with (
            patch("suplex.suplex_modules.submodules.collage.sg.TextElement") as mock_text,
            patch("suplex.suplex_modules.submodules.collage.sg.SVGFigure") as mock_svg_class,
        ):
            mock_new_svg = MagicMock()
            mock_svg_class.return_value = mock_new_svg
            result = add_title_to_svg(
                mock_svg_figure, "Test Title", TITLE_POSITION.TOP, COLOR.BLACK, font_size=14
            )
            assert result != mock_svg_figure
            mock_text.assert_called_once()

    def test_create_collage_empty_list(self):
        """Empty images list should return minimal SVG."""
        fig = create_collage([])
        assert isinstance(fig, sg.SVGFigure)

    def test_create_collage_full_pipeline(self, mock_pil_image):
        """End-to-end collage creation with all steps mocked."""
        with (
            patch("suplex.suplex_modules.submodules.collage.format_image_to_svg") as mock_format,
            patch("suplex.suplex_modules.submodules.collage.scale_svgs") as mock_scale,
            patch("suplex.suplex_modules.submodules.collage.add_padding_to_svgs") as mock_pad,
            patch("suplex.suplex_modules.submodules.collage.get_gridded_svgs") as mock_grid,
            patch("suplex.suplex_modules.submodules.collage.get_svg_array_for_svgs") as mock_array,
            patch(
                "suplex.suplex_modules.submodules.collage.generate_collage_figure"
            ) as mock_generate,
            patch("suplex.suplex_modules.submodules.collage.add_title_to_svg") as mock_title,
        ):
            mock_svg = Mock()
            mock_format.return_value = mock_svg
            mock_scale.return_value = [mock_svg]
            mock_pad.return_value = [mock_svg]
            mock_grid.return_value = [mock_svg]
            mock_array.return_value = [[mock_svg]]
            mock_generate.return_value = mock_svg
            mock_title.return_value = mock_svg

            result = create_collage([mock_pil_image], columns=3)
            assert result == mock_svg


class TestCollage:
    """Tests for the Collage UI/settings class."""

    def test_collage_init_default(self):
        """Default initialization should set expected defaults when show_all_options=True."""
        collage = Collage(show_all_options=True)
        assert collage.layout == COLLAGE_LAYOUT.GRID_EQUAL_ALL
        assert collage.columns == 1

    def test_collage_get_ui(self):
        """UI should return a valid VBox."""
        collage = Collage(show_all_options=True)
        ui = collage.get_ui()
        assert isinstance(ui, widgets.VBox)

    def test_collage_generate_collage_with_overrides(self, mock_pil_image):
        """generate_collage should respect explicit parameter overrides."""
        collage = Collage(show_all_options=True)
        with patch("suplex.suplex_modules.submodules.collage.create_collage") as mock_create:
            mock_create.return_value = Mock()
            result = collage.generate_collage(
                images=[mock_pil_image],
                layout=COLLAGE_LAYOUT.MOSAIC_EQUAL_ALL,
                columns=4,
                title="Test Collage",
            )
            assert result == mock_create.return_value
            mock_create.assert_called_once()
            call_args = mock_create.call_args[1]
            assert call_args["layout"] == COLLAGE_LAYOUT.MOSAIC_EQUAL_ALL
            assert call_args["columns"] == 4
            assert call_args["title"] == "Test Collage"

    def test_collage_active_widgets_respect_enabled_flags(self):
        """Only enabled options should appear in active_widgets."""
        collage = Collage(layouts=[COLLAGE_LAYOUT.GRID_EQUAL_ALL], show_all_options=False)
        active = collage.get_active_widgets()
        assert len(active) == 1
        assert active[0] == collage.get_layout_dropdown()
