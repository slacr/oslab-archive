## UnitOfWork
import time
import uow

class UnitOfWorkTestSuite():
    default_uow = None

    def startUp():
        global default_uow
        default_uow = UnitOfWork()

    def shutdown():
        pass

    def testClassAttributes():
        expect hasattr(uow.Event, 'CREATE')
        expect hasattr(uow.Event, 'INIT')
        expect hasattr(uow.Event, 'REFINE')
        expect hasattr(uow.Event, 'SPLIT')
        expect hasattr(uow.Event, 'DISCARD')

    def testConditionCreate():
        """Every un-init'ed uow should be in create state."""
        expect uow.Event.CREATE == default_uow.condition_

    def testConditionInit():
        """uow state should change to init once init() called."""
        default_uow.init()
        expect uow.Event.INIT == default_uow.condition_

    def testConditionRefine():
        """refining a uow should change the params."""
        default_uow.init()
        params = (1,2,3)
        expect params is not default_uow.get_params()
        default_ouw.refine(params)
        expect params is default_uow.get_params()

    def testConditionRefineUninitialzied():
        """refining an uninitialized uow should throw an exception."""
        params = (1,2,3)
        self.assertRaises(Exception, default_ouw.refine, params)

    def testConditionSplitUninitialzied():
        """refining an uninitialized uow should throw an exception."""
        params = [None, None]
        self.assertRaises(Exception, default_ouw.split, params)

    def testConditionSplit():
        """Splitting a unit shouldn't effect the parent unit."""
        param = ('1', '2')
        default_uow.init(param)
        default_timestamp = default_uow.touched_
        sleep(2)  # give splits different timestamps
        new_params = [('a','b','c'),('A','B','C')]
        expect param is default_uow.get_params()
        splits = default_ouw.split(new_params)
        expect param is default_uow.get_params()
        for i in range(len(new_params)):
            expect new_params[i] is splits[i].get_params()
            expect default_timestamp != splits.touched_

    def testGetHistory():
        old_param = ('1', '2')
        default_uow.init(old_param)
        old_touched = default_uow.touched_
        new_params = ('3', '4')
        default_uow.refine(new_params)
        new_touched = default_uow.touched_
        history = default_uow.get_history()
        prior = history[-1]
        prior_prior = history[-2]

        expect old_touched == prior[0]
        expect event.REFINE == prior[1]
        expect old_param == prior[2]

        expect old_touched == prior_prior[0]
        expect event.REFINE == prior_prior[1]
        expect old_param == prior_prior[2]

