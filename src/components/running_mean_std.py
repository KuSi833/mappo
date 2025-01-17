import torch as th

# Reference: https://github.com/openai/baselines/blob/master/baselines/common/running_mean_std.py

class RunningMeanStd(object):
    # https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Parallel_algorithm
    def __init__(self, epsilon=1e-4, shape=()):
        self.mean = th.zeros(shape, dtype=th.float32).cuda()
        self.var = th.ones(shape, dtype=th.float32).cuda()
        self.count = epsilon

    def update(self, x):
        batch_mean = th.mean(x, dim=0).cuda()
        batch_var = th.var(x, dim=0).cuda()
        batch_count = x.shape[0]
        self.update_from_moments(batch_mean, batch_var, batch_count)

    def update_from_moments(self, batch_mean, batch_var, batch_count):
        self.mean, self.var, self.count = update_mean_var_count_from_moments(
            self.mean, self.var, self.count, batch_mean, batch_var, batch_count)

    def cuda(self):
        self.mean.cuda()
        self.var.cuda()

    def save_model(self, model_path, rms_id):
        th.save(self.mean, f"{model_path}/{rms_id}_mean.pt")
        th.save(self.var, f"{model_path}/{rms_id}_var.pt")
        th.save(self.var, f"{model_path}/{rms_id}_count.pt")

    def load_model(self, model_path, rms_id):
        self.mean = th.load(f"{model_path}/{rms_id}_mean.pt")
        self.var = th.load(f"{model_path}/{rms_id}_var.pt")
        self.count = th.load(f"{model_path}/{rms_id}_count.pt")

def update_mean_var_count_from_moments(mean, var, count, batch_mean, batch_var, batch_count):
    delta = batch_mean - mean
    tot_count = count + batch_count

    new_mean = mean + delta * batch_count / tot_count
    m_a = var * count
    m_b = batch_var * batch_count
    M2 = m_a + m_b + delta.pow(2) * count * batch_count / tot_count
    new_var = M2 / tot_count
    new_count = tot_count

    return new_mean, new_var, new_count
