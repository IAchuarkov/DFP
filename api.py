from flask import Flask
from flask_restful import Api, Resource, reqparse
from PrefixSpan.prefixspan import prefixspan

app = Flask(__name__)
api = Api(app)


experiments = {}

#обертка над алгоритмом приводящая данные в нужный формат
class Algorithm:
    def __init__(self, function):
        self.algo = function

#PrefixSpan algorithm
WebPrefixSpan = Algorithm(prefixspan)


ALGORITHMS = {
    0:  WebPrefixSpan,
}


class Experiment:
    def __init__(self, exp_id, algo_id, params):
        self.exp_id = exp_id
        self.algo_id = algo_id
        self.params = params

    def display(self):
        return {
            'Experiment Id': self.exp_id,
            'Algorithm Id': self.algo_id,
            'Parameters': str(self.params) 
        }


class ExperimentDetail(Resource):
    def get(self, exp_id):
        if exp_id in experiments:
            return experiments[exp_id].display()
        return f"Experiment {exp_id} not found", 404

    def put(self, exp_id):
        if exp_id in experiments:
            return f"Experiment {exp_id} exists", 409

        parser = reqparse.RequestParser()
        parser.add_argument('algo_id', type=int)
        parser.add_argument('params')
        args = parser.parse_args(strict=True)

        #TODO: check if args are correct
        experiments[exp_id] = Experiment(exp_id, args['algo_id'], args['params'])

        #run ALGORITHMS[algo_id](args)
        return experiments[exp_id].display(), 201


class ExperimentList(Resource):
    def get(self):
        return list(experiments.keys())

api.add_resource(ExperimentList, '/experiments', '/')
api.add_resource(ExperimentDetail, '/experiments/<exp_id>')


if __name__ == "__main__":
    app.run(debug=True)