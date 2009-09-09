# -*- coding: utf-8 -*-
# This file is a readaption of network.py of mu_autocaptcha
#
# Copyright 2009 Shaun Friedle
#
# This file is part of mu_autocaptcha.
# mu_autocaptcha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mu_autocaptcha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mu_autocaptcha.  If not, see <http://www.gnu.org/licenses/>.
#
# URL: http://herecomethelizards.co.uk/mu_captcha/

from bpnn.neuron import Neuron

class Network(object):
    """
    Back propagation neural network
    """
    def __init__(self, num_inputs, num_h_neurons, num_o_neurons,
                 learning_rate = 0.1):
        """
        Create a back propagation neural network
        @param num_inputs: number of input neurons
        @param num_h_neurons: number of hidden neurons
        @param num_o_neurons: number of output neurons
        @param learning_rate: learning rate of the network
        @return: bpnn.network.Network instance
        """
        self.h_layer = self._new_layer(num_h_neurons, num_inputs)
        self.o_layer = self._new_layer(num_o_neurons, num_h_neurons)
        self.trained = False
        self.learning_rate = learning_rate
        self.error = 0

    def _new_layer(self, num_neurons, num_inputs):
        return [Neuron(num_inputs) for i in xrange(num_neurons)]

    def feed(self, inputs):
        """
        Feed the neural network with a list of inputs.
        @param inputs: a list or tuple containing inputs
        """
        h_outputs = []
        for neuron in self.h_layer:
            neuron.feed(inputs)
            h_outputs.append(neuron.output())

        for neuron in self.o_layer:
            neuron.feed(h_outputs)

    def output(self):
        """
        Get the status of the output neuron layer as list
        @return: a list() containing the value of the output neurons.
        """
        return [neuron.output() for neuron in self.o_layer]

    def test(self, inputs):
        """
        Feed the network and get the output.

        This method is simply feed() followed by output().

        @param inputs: a list or tuple containing inputs
        @return: a list() containing the value of the output neurons.
        """
        self.feed(inputs)
        return self.output()

    def train(self, inputs, target):
        """
        Train the neural network
        @param inputs: a list or tuple containing inputs
        @param target: a list() containing the value of the output neurons.
        @return: current error of the network for that input
        """
        self.feed(inputs)
        for i in xrange(len(self.o_layer)):
            o_neuron = self.o_layer[i]
            output = o_neuron.output()
            o_neuron.error = (target[i] - output) * output * (1 - output)
            h_outputs = [h_neuron.output() for h_neuron in self.h_layer]
            o_neuron.adjust_weights(h_outputs, self.learning_rate)

        for i in xrange(len(self.h_layer)):
            h_neuron = self.h_layer[i]
            h_neuron.error = 0
            for o_neuron in self.o_layer:
                h_neuron.error += o_neuron.weights[i] * o_neuron.error
            h_neuron.error *= h_neuron.output() * (1 - h_neuron.output())
            h_neuron.adjust_weights(inputs, self.learning_rate)

        self.error = 0

        for neuron in self.o_layer:
            self.error += abs(neuron.error)

        return self.error
