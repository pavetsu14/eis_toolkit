from pathlib import Path

import numpy as np
import pytest
import rasterio

from eis_toolkit.exceptions import InvalidParameterValueException, InvalidRasterBandException
from eis_toolkit.raster_processing.filters.speckle import frost_filter

parent_dir = Path(__file__).parent.parent
raster_path_single = parent_dir.joinpath("../data/remote/small_raster.tif")
raster_path_multi = parent_dir.joinpath("../data/remote/small_raster_multiband.tif")

idx_pixel_comparison = [15, 13]
expected_results = {"result": 4.762}


def test_frost_filter():
    """Test the focal filter function."""
    with rasterio.open(raster_path_single) as raster:
        # Choose large number of looks to get small noise variance
        result = frost_filter(raster, size=5, damping_factor=1)

        # Shapes and types
        assert isinstance(result, np.ndarray)
        assert result.shape == (raster.height, raster.width)

        # Values
        result_pixel = result[idx_pixel_comparison[0], idx_pixel_comparison[1]]
        np.testing.assert_almost_equal(result_pixel, expected_results["result"], decimal=3)


def test_number_bands():
    """Test if the number of bands is correct."""
    with rasterio.open(raster_path_multi) as raster:
        with pytest.raises(InvalidRasterBandException):
            frost_filter(raster)


def test_window_size():
    """Test if the window size is correct."""
    with rasterio.open(raster_path_single) as raster:
        with pytest.raises(InvalidParameterValueException):
            # Too small
            frost_filter(raster, size=0)

            # Even number
            frost_filter(raster, size=4)


def test_damping_factor():
    """Test if input parameters are correct."""
    with rasterio.open(raster_path_single) as raster:
        with pytest.raises(InvalidParameterValueException):
            frost_filter(raster, damping_factor=-1)
