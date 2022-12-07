
from cc3d import CompuCellSetup
        

from exampleSteppables import exampleSteppable

CompuCellSetup.register_steppable(steppable=exampleSteppable(frequency=1))


CompuCellSetup.run()
