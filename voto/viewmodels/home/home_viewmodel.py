from voto.viewmodels.shared.viewmodelbase import ViewModelBase
import voto.services.profile_service as profile_services


class IndexViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        totals = profile_services.totals()
        self.profile_count = totals

