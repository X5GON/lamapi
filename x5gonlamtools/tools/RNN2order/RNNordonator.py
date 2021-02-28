import torch
import torch.nn as nn


class RNNordonator(nn.Module):
    def __init__(self, input_dim, hidden_dim, *,
                 nb_rnn_layers=4,
                 nb_fnn_layers=4,
                 fnn_activation_fonction="ReLU",
                 bias=True,
                 rnn_type="LSTM",
                 embedding_dropout=0.2,
                 dropout=0.1,
                 embedding_combination="concatenation"):
        super(RNNordonator, self).__init__()
        self._params = {"input_dim": input_dim,
                        "hidden_dim": hidden_dim,
                        "nb_rnn_layers": nb_rnn_layers,
                        "nb_fnn_layers": nb_fnn_layers,
                        "fnn_activation_fonction": fnn_activation_fonction,
                        "bias": bias,
                        "rnn_type": rnn_type,
                        "dropout": dropout,
                        "embedding_combination": embedding_combination}
        if fnn_activation_fonction == "GELU":
            def fnn_activation_fonction():
                 return (nn.GELU(),)
        elif fnn_activation_fonction == "ReLU":
            def fnn_activation_fonction():
                 return (nn.ReLU(), nn.Dropout(dropout))
        else:
            raise RuntimeError("Only GELU and ReLU are currently supported")
        self.embedding_dropout = nn.Dropout(embedding_dropout)
        if rnn_type == "LSTM":
            # The LSTM takes word embeddings as inputs, and outputs hidden states
            # with dimensionality hidden_dim.
            self._rnn = nn.LSTM(input_dim, hidden_dim,
                                num_layers=nb_rnn_layers,
                                bias=bias,
                                dropout=dropout)
        elif rnn_type == "GRU":
            self._rnn = nn.GRU(input_dim, hidden_dim,
                               num_layers=nb_rnn_layers,
                               bias=bias,
                               dropout=dropout)
        else:
            raise RuntimeError("rnn_type shall be 'LSTM' or 'GRU'")
        seq = (nn.Linear(2 * hidden_dim, hidden_dim, bias=bias),
               *fnn_activation_fonction())
        for _ in range(0, nb_fnn_layers):
            seq += (nn.Linear(hidden_dim, hidden_dim, bias=bias),
                    *fnn_activation_fonction())
        seq += (nn.Linear(hidden_dim, 1, bias=bias),
                nn.Sigmoid())
        self._fnn = nn.Sequential(*seq)

    @property
    def params(self):
        return self._params

    def init_hidden_states(self, batch_size):
        if self._params["rnn_type"] == "LSTM":
            return (torch.zeros(self._params["nb_rnn_layers"],
                                batch_size,
                                self._params["hidden_dim"]),
                    torch.zeros(self._params["nb_rnn_layers"],
                                batch_size,
                                self._params["hidden_dim"]))
        elif self._params["rnn_type"] == "GRU":
            return (torch.zeros(self._params["nb_rnn_layers"],
                                batch_size,
                                self._params["hidden_dim"]))

    def __combine_embedding(self, last_layer1, last_layer2):
        if self._params["embedding_combination"] == "combination":
            mult_emb = last_layer1 * last_layer2
            abs_emb = torch.abs(last_layer1 - last_layer2)
            # print("mult_emb", mult_emb.shape)
            # print("abs_emb", abs_emb.shape)
            return torch.cat((mult_emb, abs_emb), 1)
        elif self._params["embedding_combination"] == "concatenation":
            return torch.cat((last_layer1, last_layer2), 1)
        else:
            RuntimeError("embedding_combination should have value in" +
                         "['combination', 'concatenation']")

    def forward(self, x1, x2):
        assert x1.shape[1] == x2.shape[1]
        batch_size = x1.shape[1]
        x1 = self.embedding_dropout(x1)
        x2 = self.embedding_dropout(x2)
        rnn_out1, _ = self._rnn(x1, self.init_hidden_states(batch_size))
        rnn_out2, _ = self._rnn(x2, self.init_hidden_states(batch_size))
        # print("rnn_out1", rnn_out1.shape)
        # print("rnn_out2", rnn_out2.shape)
        last_layer1 = rnn_out1[-1].view(batch_size, -1)
        last_layer2 = rnn_out2[-1].view(batch_size, -1)
        # print("last_layer1", last_layer1.shape)
        # print("last_layer2", last_layer2.shape)
        linear_input = self.__combine_embedding(last_layer1, last_layer2)
        # print("linear_input", linear_input.shape)
        y_pred = self._fnn(linear_input)
        return y_pred.view(-1)

    def save(self, path):
        torch.save(self.state_dict(), path)
