import workflow

"""

"""

    state_path = '...'
    state_id = '...'
    invalid_state_id = '...'
    invalid_state_path = '...'
    sieve_path = './test_data/'
    default_sieve = 'default_sieve'
    incompatible_sieve = 'cranky_sieve'

    def testExpectedClassAttributes():
        expect hasattr(workhorse, 'NoSieves')
        expect hasattr(workhorse, 'BadSieve')
        expect hasattr(workhorse, 'InvalidInitState')

    def testWorkHorseConstructor():
        wh = workhorse.WorkHorse(state_path, state_id)
        expect wh is not None

    def testWorkHorseConstructorNoStages():
        wh = workhorse.WorkHorse(state_path, state_id)
        expectRaises(workhorse.NoSieves, wh.init, ())

    def testWorkHorseConstructorValidStateId():
        wh = workhorse.WorkHorse(state_path, valid_state_id)
        wh.load_sieves(sieve_path, [default_sieve])
        wh.init()

    def testWorkHorseConstructorValidStateIdReset():
        wh = workhorse.WorkHorse(state_path, valid_state_id)
        wh.load_sieves(sieve_path, [default_sieve])
        wh.reset()
        os.system('check to verify old state files still exist.')

    def testWorkHorseConstructorInvalidStatePath():
        wh = workhorse.WorkHorse(invalid_state_path, state_id)
        wh.load_sieves(sieve_path, [default_sieve])
        expectRaises(workhorse.InvalidInitState, wh.init, ())

    def testWorkHorseConstructorInvalidStatePathReset():
        wh = workhorse.WorkHorse(invalid_state_path, state_id)
        wh.load_sieves(sieve_path, [default_sieve])
        expectRaises(workhorse.InvalidInitState, wh.reset, ())

    def testWorkHorseConstructorInvalidStateId():
        wh = workhorse.WorkHorse(state_path, invalid_state_id)
        wh.load_sieves(sieve_path, [default_sieve])
        expectRaises(workhorse.InvalidInitState, wh.init, ())

    def testWorkHorseConstructorInvalidStateIdReset():
        wh = workhorse.WorkHorse(state_path, invalid_state_id)
        wh.load_sieves(sieve_path, [default_sieve])
        wh.reset()

    def testWorkHorseConstructorIncompatibleInit():
        wh = workhorse.WorkHorse(state_path, valid_state_id)
        wh.load_sieves(sieve_path, [cranky_sieve])
        expectRaises(workhorse.InvalidInitState, wh.init, ())

    def testWorkHorseConstructorIncompatibleReset():
        wh = workhorse.WorkHorse(state_path, valid_state_id)
        wh.load_sieves(sieve_path, [cranky_sieve])
        wh.reset()
        os.system('check to verify old state files still exist.')


def testWorkHorseMethods():
    sieve_path = './test_data'
    sieve_list = ['dummy_sieve_A', 'dummy_sieve_B']
    wh = None

    def startUp():
        wh = workhorse.WorkHorse()

    def tearDown():
        pass

    def testWorkHorseAddUninitializedSieve():
        sieve = sieve_list[0]
        s = Sieve(sieve_path, sieve)
        expectRaise(BadSieve, wh.add_sieve, (s))

    def testWorkHorseAddInitializedSieve():
        sieve = sieve_list[0]
        s = Sieve(sieve_path, sieve)
        s.init()
        wh.add_sieve(s)
        wh.reset()

    def testWorkHorseLoadSieves():
        wh.load_sieves(sieve_path, sieve_list)   # loads and initializes sieves
        wh.reset()

def testWorkHorseOperations():
    sieve_list = ['dummy_sieve_A', 'dummy_sieve_B']
    wh = None

    def startUp():
        wh = workhorse.WorkHorse()
        wh.load_sieves(sieve_list)
        wh.reset()

    def tearDown():
        pass
        
    def testWorkHorseKickIt():
        wh.restart()

    """Add a sieve stage to a workhorse."""
    """? Remove a sieve? No."""
    """? Reorder sieves? No."""
    """? Reload/Replace a sieve? No."""
    """? Disable/Enable a sieve? Probably maybe."""
    """How much have you been given?"""
    """How much work have you done?"""
    """What work is made it past which sieve?"""
    """What work is dying/retrying a lot?"""
    """What work was discarded by a sieve?"""
    """What new work originated in a sieve?"""
    """How far have you proceeded with a sieve?"""



def testSieve():
    """
      sieve_path = ''
      sieve_name = ''
      sieve_params = '?'
      new_f = SieveConstructor(sieve_path, sieve_name, sieve_params)
      new_f.init(state_path, state_id)   # actually loads the indiciated module
      new_f.reset(state_path, state_id)  # starts fresh
      new_f.do_it(worker)
    """
    def testExpectedClassAttributes():
        expect sieve.InvalidSieve is not None

    def testSieveConstructor():
        sieve_path = './test_data/'
        sieve_name = 'basic_sieve'  # ./test_data/basic_sieve.py
        new_f = Sieve(sieve_path, sieve_name)
        expect new_f is not None

    def testSieveConstructorMissingSieve():
        sieve_path = './test_data/'
        sieve_name = 'neverheardofme'  # ./test_data/basic_sieve.py
        new_f = Sieve(sieve_path, sieve_name)
        expect new_f is not None
        expectRaise(sieve.InvalidSieve, new_f.init, ())

    def testSieveConstructorCantRead():
        sieve_path = './test_data/'
        sieve_name = 'writeonly'
        new_f = Sieve(sieve_path, sieve_name)
        expect new_f is not None
        expectRaise(sieve.InvalidSieve, new_f.init, ())

    def testSieveConstructorNotExecutable():
        sieve_path = './test_data/'
        sieve_name = 'noexec'
        new_f = Sieve(sieve_path, sieve_name)
        expect new_f is not None

def testSieveState():
    sieve_path = './test_data/'
    sieve_name = 'default_sieve'
    state_path = '...'
    state_id = '...'
    invalid_state_id = '...'
    invalid_state_path = '...'
    f = None

    def startUp():
        f = Sieve(sieve_path, sieve_name)

    def tearDown():
        pass

    def testSieveState():
        f.init(state_path, state_id)

    def testSieveInvalidStatePathInit():
        expectRaise(sieve.InvalidState, f.init, (state_path, invalid_state_id))

    def testSieveInvalidStatePathReset():
        expectRaise(sieve.InvalidState, f.reset, (state_path, invalid_state_id))

    def testSieveInvalidStateIdInit():
        expectRaise(sieve.InvalidState, f.init, (state_path, invalid_state_id))

    def testSieveInvalidStateIdReset():
        f.reset(state_path, invalid_state_id)


def testSieveMethods():
    sieve_path = './test_data/'
    sieve_name = 'default_sieve'
    f = None

    def startUp():
        f = Sieve(sieve_path, sieve_name)

    def tearDown():
        pass

    """ select a random worker for stage?"""
    """ log to stage-specific log file?"""
    """ how much work to-be-done is in this sieve stage."""
    """ how much work in this sieve is being done right now."""
    """ predicate: is there work to be done in this sieve?"""
    """ predicate: is there work being done in this sieve?"""
    """ predicate: is there work completed by this sieve?"""
    """ some way to get get the completed work from the sieve."""
    """ some way to retry work that failed in this sieve."""
    """ some way to schedule backup-work that is taking too long in this sieve."""
    """ some way to move work from unassigned to assigned."""
    """ Q:explicit way to re-load the module?"""

    def testSieveAttributes():
        expect hasattr(f, 'name')
        expect hasattr(f, 'module')
        expect hasattr(f, 'initialized')

    def testSieveName():
        expect f.name == 'default_sieve'

    def testSieveInitialized():
        expect f.initialized is None
        f.init()
        expect f.initialized        

    def testSieveModule():
        expect type(f.module) == 'None'
        f.init()
        expect type(f.module) == 'module'

    def testSieveAppearance():
        stringified = str(f)
        expect stringified == "<name = 'default_sieve', sieve_name = 'default_sieve.py', sieve_path = './test_data', module = None >"
        f.init()
        stringified = str(f)
        expect stringified == "<name = 'default_sieve', sieve_name = 'default_sieve.py', sieve_path = './test_data', module = None >"

def testRemoteWorker():



def testRPC():


