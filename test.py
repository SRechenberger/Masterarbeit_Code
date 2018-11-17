import src.experiment.experiment as exp

e = exp.StaticExperiment('test_files', 1, 'gsat', poolsize = 1)
e.run_experiment()
e.save_results()
