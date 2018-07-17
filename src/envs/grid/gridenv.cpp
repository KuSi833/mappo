#include <iostream>
#include <torch/torch.h>
#include <vector>

using namespace at; // using ATen https://github.com/pytorch/pytorch/tree/master/aten
using namespace std;

bool DEBUG = true;

class GridEnv {

    public:
        GridEnv(){}
        ~GridEnv(){}

    protected:
        unsigned short batch_size;
        unsigned short grid_dim_x;
        unsigned short grid_dim_y;

        bool is_gpu;
        unsigned short device_id;

        string grid_geometry;
        Tensor grid;

        void create_grid(void);
};

void GridEnv::create_grid(void) {
    auto deviceFunc = CUDA;
    cout << this->is_gpu << "||";
    if (!this->is_gpu) deviceFunc = CPU;

    auto dataType = kLong;
    if (sizeof(char*) == 4) dataType = kInt;

    //this->grid = deviceFunc(dataType).zeros({this->batch_size, this->grid_dim_x, this->grid_dim_y});
    this->grid = CUDA(dataType).zeros({this->batch_size, this->grid_dim_x, this->grid_dim_y});

    if (DEBUG) cout << "INIT GRID";
}


class PredatorPreyEnv : public GridEnv {

    public:
        PredatorPreyEnv(unsigned short, unsigned short, unsigned short, unsigned short, unsigned short, unsigned char, unsigned char, string grid_geometry);
        ~PredatorPreyEnv(){}

    private:
        unsigned short n_prey;
        unsigned short n_predators;
        bool is_gpu;
        unsigned short device_id;

        void init_grid(void);
};

PredatorPreyEnv::PredatorPreyEnv(unsigned short batch_size,
                                 unsigned short grid_dim_x,
                                 unsigned short grid_dim_y,
                                 unsigned short n_prey,
                                 unsigned short n_predators,
                                 unsigned char is_gpu,
                                 unsigned char device_id,
                                 string grid_geometry){

    this->batch_size = batch_size;
    this->grid_dim_x = grid_dim_x;
    this->grid_dim_y = grid_dim_y;

    this->n_prey = n_prey;
    this->n_predators = n_predators;

    this->is_gpu = is_gpu;
    this->device_id = device_id;

    this->grid_geometry = grid_geometry;

    this->create_grid();
    this->init_grid();
}

void PredatorPreyEnv::init_grid(){

    cout << this->grid[0][0][0];

}

// void PredatorPreyEnv::Test(void){
//    std::cout << "HELLO!";
//    throw runtime_error("hello edar");
// }


PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    py::class_<PredatorPreyEnv> animal(m, "PredatorPreyEnv");
    animal
        .def(py::init<unsigned short,
                      unsigned short,
                      unsigned short,
                      unsigned short,
                      unsigned short,
                      unsigned char,
                      unsigned char,
                      string>());
}

        // .def("Test", &PredatorPreyEnv::Test);

/*// s'(z) = (1 - s(z)) * s(z)
at::Tensor d_sigmoid(at::Tensor z) {
  auto s = at::sigmoid(z);
  return (1 - s) * s;
}

// tanh'(z) = 1 - tanh^2(z)
at::Tensor d_tanh(at::Tensor z) {
  return 1 - z.tanh().pow(2);
}

// elu'(z) = relu'(z) + { alpha * exp(z) if (alpha * (exp(z) - 1)) < 0, else 0}
at::Tensor d_elu(at::Tensor z, at::Scalar alpha = 1.0) {
  auto e = z.exp();
  auto mask = (alpha * (e - 1)) < 0;
  return (z > 0).type_as(z) + mask.type_as(z) * (alpha * e);
}*/

/*std::vector<at::Tensor> lltm_forward(
    at::Tensor input,
    at::Tensor weights,
    at::Tensor bias,
    at::Tensor old_h,
    at::Tensor old_cell) {
  auto X = at::cat({old_h, input}, 1);

  auto gate_weights = at::addmm(bias, X, weights.transpose(0, 1));
  auto gates = gate_weights.chunk(3, 1);

  auto input_gate = at::sigmoid(gates[0]);
  auto output_gate = at::sigmoid(gates[1]);
  auto candidate_cell = at::elu(gates[2], 1.0);

  auto new_cell = old_cell + candidate_cell * input_gate;
  auto new_h = at::tanh(new_cell) * output_gate;

  return {new_h,
          new_cell,
          input_gate,
          output_gate,
          candidate_cell,
          X,
          gate_weights};
}

std::vector<at::Tensor> lltm_backward(
    at::Tensor grad_h,
    at::Tensor grad_cell,
    at::Tensor new_cell,
    at::Tensor input_gate,
    at::Tensor output_gate,
    at::Tensor candidate_cell,
    at::Tensor X,
    at::Tensor gate_weights,
    at::Tensor weights) {
  auto d_output_gate = at::tanh(new_cell) * grad_h;
  auto d_tanh_new_cell = output_gate * grad_h;
  auto d_new_cell = d_tanh(new_cell) * d_tanh_new_cell + grad_cell;

  auto d_old_cell = d_new_cell;
  auto d_candidate_cell = input_gate * d_new_cell;
  auto d_input_gate = candidate_cell * d_new_cell;

  auto gates = gate_weights.chunk(3, 1);
  d_input_gate *= d_sigmoid(gates[0]);
  d_output_gate *= d_sigmoid(gates[1]);
  d_candidate_cell *= d_elu(gates[2]);

  auto d_gates =
      at::cat({d_input_gate, d_output_gate, d_candidate_cell}, 1);

  auto d_weights = d_gates.t().mm(X);
  auto d_bias = d_gates.sum(0, true);

  auto d_X = d_gates.mm(weights);
  const auto state_size = grad_h.size(1);
  auto d_old_h = d_X.slice(1, 0, state_size);
  auto d_input = d_X.slice(1, state_size);

  return {d_old_h, d_input, d_weights, d_bias, d_old_cell};
}*/
/*
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
  m.def("forward", &lltm_forward, "LLTM forward");
  m.def("backward", &lltm_backward, "LLTM backward");
}*/