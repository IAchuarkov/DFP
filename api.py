#!/usr/bin/env python3

from flask import Flask
from flask_restful import Api, Resource, reqparse
from PrefixSpan.prefixspan import PrefixSpan
from FIN.fin import FIN

app = Flask(__name__)
api = Api(app)


experiments = {}


ALGORITHMS = {
    0:  PrefixSpan,
    1:  FIN,
    'PrefixSpan': 0,
    'FIN' : 1,
}

FIN_EXAMPLE_DATA = [
    ['a', 'c', 'g', 'f'],
    ['e', 'a', 'c', 'b'],
    ['e', 'c', 'b', 'i'],
    ['b', 'f', 'h'],
    ['b', 'f', 'e', 'c', 'd']
]

def get_data(exp):
    if exp.algo_id == ALGORITHMS['FIN']:
        return FIN_EXAMPLE_DATA

    return []

class Experiment:
    def __init__(self, exp_id, algo_id, min_support):
        self.exp_id = exp_id
        self.algo_id = algo_id
        self.min_support = min_support
        self.results = []

        self.execute()

    def display(self):

        res_dict = {
            'Experiment Id': self.exp_id,
            'Algorithm Id': self.algo_id,
            'Minimal Support': self.min_support
        }
        
        res_dict.update({ 
            str(pattern.itemset) : pattern.support
             for pattern in self.result
        })
        
        return res_dict

    
    def execute(self):
        data = get_data(self)
        
        self.result = FIN(data, self.min_support)




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
        parser.add_argument('min_support', type=float)
        args = parser.parse_args(strict=True)

        experiments[exp_id] = Experiment(exp_id, args['algo_id'], args['min_support'])

        return experiments[exp_id].display(), 201


class ExperimentList(Resource):
    def get(self):
        return list(experiments.keys())

api.add_resource(ExperimentList, '/experiments', '/')
api.add_resource(ExperimentDetail, '/experiments/<exp_id>')


if __name__ == "__main__":
    app.run(debug=True)