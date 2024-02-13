import os

import numpy as np
import pytest
import tensorflow as tf
from sklearn.preprocessing import StandardScaler

from eis_toolkit.exceptions import InvalidArgumentTypeException
from eis_toolkit.prediction.cnn_classification_and_probability import (
    run_inference_for_classification,
    run_inference_for_regression,
)
from eis_toolkit.prediction.model_performance_estimation import performance_model_estimation
from eis_toolkit.transformations.normalize_data import normalize_the_data
from eis_toolkit.transformations.one_hot_encoding import one_hot_encode


def test_train_CNN_classifier_with_categorical_crossentropy():
    """Test for classification."""
    data = np.load(f'{os.path.join("data", "data.npy")}')
    labels = np.load(f'{os.path.join("data", "labels.npy")}')

    # do the encoding
    encoded_labels = one_hot_encode(labels, sparse_output=False)

    # create a scaler agent
    scaler_agent = StandardScaler()
    scaler_agent.fit(data.reshape(-1, data.shape[-1]))

    # make cv
    selected_cv = performance_model_estimation(cross_validation_type="SKFOLD", number_of_split=5)

    stacked_true, stacked_predicted = None, None

    for i, (train_idx, validation_idx) in enumerate(selected_cv.split(data, labels)):

        x_train = normalize_the_data(scaler_agent=scaler_agent, data=data[train_idx])
        y_train = encoded_labels[train_idx]

        x_validation = normalize_the_data(scaler_agent=scaler_agent, data=data[validation_idx])
        y_validation = encoded_labels[validation_idx]

        cnn_model, predicted_labels, score = run_inference_for_classification(
            X=x_train,
            y=y_train,
            validation_split=0.2,
            validation_data=(x_validation, y_validation),
            batch_size=32,
            epochs=10,
            conv_list=[4, 8],
            neuron_list=[8],
            input_shape_for_cnn=(x_train.shape[1], x_train.shape[2], x_train.shape[3]),
            convolutional_kernel_size=(x_train.shape[3], x_train.shape[3]),
            last_activation_layer="softmax",
            loss_function=tf.keras.losses.CategoricalCrossentropy(),
        )

        if stacked_true is None:
            stacked_true = np.argmax(y_validation, axis=1)
        else:
            stacked_true = np.concatenate((stacked_true, np.argmax(y_validation, axis=1)))

        if stacked_predicted is None:
            stacked_predicted = np.argmax(predicted_labels, axis=1)
        else:
            stacked_predicted = np.concatenate((stacked_predicted, np.argmax(predicted_labels, axis=1)))

    assert stacked_true.shape != 0 and stacked_predicted.shape != 0


def test_train_CNN_classifier_with_binary_crossentropy():
    """Test for classification with binary cross entropy."""
    data = np.load(f'{os.path.join("data", "data.npy")}')
    labels = np.load(f'{os.path.join("data", "labels.npy")}')

    # create a scaler agent
    scaler_agent = StandardScaler()
    scaler_agent.fit(data.reshape(-1, data.shape[-1]))

    # make cv
    selected_cv = performance_model_estimation(cross_validation_type="SKFOLD", number_of_split=5)

    stacked_true, stacked_predicted = None, None

    for i, (train_idx, validation_idx) in enumerate(selected_cv.split(data, labels)):

        x_train = normalize_the_data(scaler_agent=scaler_agent, data=data[train_idx])
        y_train = labels[train_idx]

        x_validation = normalize_the_data(scaler_agent=scaler_agent, data=data[validation_idx])
        y_validation = labels[validation_idx]

        cnn_model, predicted_labels, score = run_inference_for_classification(
            X=x_train,
            y=y_train,
            validation_split=0.2,
            validation_data=(x_validation, y_validation),
            batch_size=32,
            epochs=10,
            conv_list=[4, 8],
            neuron_list=[8],
            input_shape_for_cnn=(x_train.shape[1], x_train.shape[2], x_train.shape[3]),
            convolutional_kernel_size=(x_train.shape[3], x_train.shape[3]),
            last_activation_layer="sigmoid",
            loss_function=tf.keras.losses.BinaryCrossentropy(),
            output_units=1,
        )

        if stacked_true is None:
            stacked_true = y_validation
        else:
            stacked_true = np.concatenate((stacked_true, y_validation))

        if stacked_predicted is None:

            stacked_predicted = (predicted_labels >= 0.5).astype(int)
        else:
            stacked_predicted = np.concatenate((stacked_predicted, (predicted_labels >= 0.5).astype(int)))

    assert stacked_true.shape != 0 and stacked_predicted.shape != 0


def test_train_CNN_regressor():
    """Test for classification."""
    data = np.load(f'{os.path.join("data", "data.npy")}')
    labels = np.load(f'{os.path.join("data", "labels.npy")}')

    # create a scaler agent
    scaler_agent = StandardScaler()
    scaler_agent.fit(data.reshape(-1, data.shape[-1]))

    # make cv
    selected_cv = performance_model_estimation(cross_validation_type="SKFOLD", number_of_split=5)

    stacked_true, stacked_predicted = None, None

    for i, (train_idx, validation_idx) in enumerate(selected_cv.split(data, labels)):

        x_train = normalize_the_data(scaler_agent=scaler_agent, data=data[train_idx])
        y_train = labels[train_idx]

        x_validation = normalize_the_data(scaler_agent=scaler_agent, data=data[validation_idx])
        y_validation = labels[validation_idx]

        cnn_model, predicted_labels, probabilities, score = run_inference_for_regression(
            X=x_train,
            y=y_train,
            validation_split=0.2,
            validation_data=(x_validation, y_validation),
            batch_size=32,
            epochs=10,
            conv_list=[4, 8],
            neuron_list=[8],
            input_shape_for_cnn=(x_train.shape[1], x_train.shape[2], x_train.shape[3]),
            convolutional_kernel_size=(x_train.shape[3], x_train.shape[3]),
            threshold=0.5,
            last_activation_layer=None,
            loss_function=tf.keras.losses.MeanAbsoluteError(),
            output_units=1,
        )

        if stacked_true is None:
            stacked_true = y_validation
        else:
            stacked_true = np.concatenate((stacked_true, y_validation))
        if stacked_predicted is None:
            stacked_predicted = predicted_labels
        else:
            stacked_predicted = np.concatenate((stacked_predicted, predicted_labels))

    assert stacked_true.shape[0] != 0 and stacked_predicted.shape[0] != 0


def test_invalid_convolutional_layer():
    """Test invalid convolutional layer."""
    with pytest.raises(InvalidArgumentTypeException):
        x_train = np.load(f'{os.path.join("data", "data.npy")}')
        y_train = np.load(f'{os.path.join("data", "labels.npy")}')

        cnn_model, predicted_labels, score = run_inference_for_classification(
            X=x_train,
            y=y_train,
            validation_split=0.2,
            validation_data=None,
            batch_size=32,
            epochs=10,
            conv_list=[],
            neuron_list=[8],
            input_shape_for_cnn=(x_train.shape[1], x_train.shape[2], x_train.shape[3]),
            convolutional_kernel_size=(x_train.shape[3], x_train.shape[3]),
        )


def test_invalid_neurons_layer():
    """Test invalid neuron layers."""
    with pytest.raises(InvalidArgumentTypeException):
        x_train = np.load(f'{os.path.join("data", "data.npy")}')
        y_train = np.load(f'{os.path.join("data", "labels.npy")}')

        cnn_model, predicted_labels, score = run_inference_for_classification(
            X=x_train,
            y=y_train,
            validation_split=0.2,
            validation_data=None,
            batch_size=32,
            epochs=10,
            conv_list=[8],
            neuron_list=[],
            input_shape_for_cnn=(x_train.shape[1], x_train.shape[2], x_train.shape[3]),
            convolutional_kernel_size=(x_train.shape[3], x_train.shape[3]),
        )


def test_invalid_parameters_dropout_exception():
    """Invalid dropout test."""
    with pytest.raises(InvalidArgumentTypeException):
        x_train = np.load(f'{os.path.join("data", "data.npy")}')
        y_train = np.load(f'{os.path.join("data", "labels.npy")}')

        cnn_model, predicted_labels, score = run_inference_for_classification(
            X=x_train,
            y=y_train,
            validation_split=None,
            validation_data=None,
            batch_size=32,
            epochs=10,
            conv_list=[8],
            neuron_list=[8],
            input_shape_for_cnn=(x_train.shape[1], x_train.shape[2], x_train.shape[3]),
            convolutional_kernel_size=(x_train.shape[3], x_train.shape[3]),
            dropout_rate=-10.0,
        )


def test_invalid_parameters_inputs_exception():
    """Invalid inputs test."""
    with pytest.raises(InvalidArgumentTypeException):
        x_train = np.load(f'{os.path.join("data", "data.npy")}')

        cnn_model, predicted_labels, score = run_inference_for_classification(
            X=np.array([]),
            y=np.array([]),
            validation_split=None,
            validation_data=None,
            batch_size=32,
            epochs=10,
            conv_list=[8],
            neuron_list=[8],
            input_shape_for_cnn=(x_train.shape[1], x_train.shape[2], x_train.shape[3]),
            convolutional_kernel_size=(x_train.shape[3], x_train.shape[3]),
            dropout_rate=None,
        )
