import torch

from x5gonwp3tools.tools.RNN2order.RNNordonator import RNNordonator


def reordonize(model, cd2v1, cd2v2):
    cd2v1 = torch.tensor(cd2v1)[:, None, :]
    cd2v2 = torch.tensor(cd2v2)[:, None, :]
    pred = model(cd2v1, cd2v2).item()
    return {'pred_score': pred,
            'c_scores': {}}


def load_model(model_path):
    model_prop = torch.load(model_path)
    model = RNNordonator(**model_prop["model_params"])
    model.load_state_dict(model_prop['model_state_dict'])
    model.eval()
    return model
