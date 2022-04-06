import flask
from voto.infrastructure.view_modifiers import response
from voto.viewmodels.home.home_viewmodel import IndexViewModel
blueprint = flask.Blueprint('home', __name__, template_folder='templates')


@blueprint.route('/')
@response(template_file='home/index.html')
def index():
    vm = IndexViewModel()
    return vm.to_dict()
