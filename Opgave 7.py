import pyomo.environ as pyomo  # Used for modelling the IP
import readAndWriteJson as rwJson  # Used to read data from Json file
from termcolor import colored

def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    return data


def buildModel(data: dict) -> pyomo.ConcreteModel():
    # Define the model
    model = pyomo.ConcreteModel()
    # Copy data to model
    model.kommuner = data['municipalities']
    model.fasteomkostninger = data['basis_price']
    model.mia = 1000000000
    model.basiskapacitet = data['basis_capacity']
    model.ekstraomkostninger = data['ext_price']
    model.Defterspørgsel2022 = data['inhab2022']
    model.Defterspørgsel2030 = data['inhab2030']
    model.distances = data['distances']
    model.travel_times = data['travel_times']
    model.AntalSygehuse = data['p']
    model.RangeAntalKommuner = range(0,len(model.kommuner))
    model.budget_begrænsning = 29849347500
    model.a = data['cover_matrix']
    model.b = data['b']

    # Define variables
    model.y = pyomo.Var(model.RangeAntalKommuner, within=pyomo.Binary)
    model.z = pyomo.Var(model.RangeAntalKommuner, within=pyomo.Binary)
    # Define objective function
    model.obj = pyomo.Objective(expr=sum(model.z[j] for j in model.RangeAntalKommuner), sense=pyomo.maximize)
    # Add covering constraints
    model.coveringCsts = pyomo.ConstraintList()
    for j in model.RangeAntalKommuner:
        model.coveringCsts.add(
            expr=sum(model.a[i][j] * model.y[i] for i in model.RangeAntalKommuner) >= model.b * model.z[j])
    # Add cardinality constraint
    model.cardinality = pyomo.Constraint(expr=sum(model.y[i] for i in model.RangeAntalKommuner) <= model.AntalSygehuse)
    return model

def solveModel(model: pyomo.ConcreteModel()):
 # Define a solver
    solver = pyomo.SolverFactory('cbc')
    # Solve the model
    solver.solve(model, tee=True)

def displaySolution(model: pyomo.ConcreteModel()):
    # Print optimal objective function value
    print('Optimal objective function value is', pyomo.value(model.obj))
    print('The following facilities are open:')
    for i in model.RangeAntalKommuner:
        if pyomo.value(model.y[i]) == 1:
            print(model.kommuner[i], end=',')
    print('\nCustomers are covered as follows:')
    for j in model.RangeAntalKommuner:
        if pyomo.value(model.z[j]) == 1:
            print(colored(model.kommuner[j], 'green'),end='->\t')
        else:
            print(colored(model.kommuner[j], 'red'), end='->\t')
        for i in model.RangeAntalKommuner:
            if model.a[i][j] == 1 and pyomo.value(model.y[i])==1:
                print(model.kommuner[i], end=',')
        print('')
    # Print the open facilities


def main(instance_file_name):
    data = readData(instance_file_name)
    model = buildModel(data)
    solveModel(model)
    displaySolution(model)


if __name__ == '__main__':
    instance_file_name = 'Data'
    main(instance_file_name)