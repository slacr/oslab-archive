OS Lab SVN Repository

Created: Fall 2011 (Mike Yegge)
Updated: 1.31.2012 (Jay Bolton) --fleshed out administrivia

Check out http://trac.evergreen.edu/wiki/OSLab-svn-repo-structure for the
reasoning behind this structure. (We pretty much followed the svn tutorial
verbatim for structuring our code base.)

Here's what we're aiming for:

  ../ac/os-lab/

	  private/<user>/
	         anything specific you may want to commit, like your personal
		 config files
	  public/courses/
	  public/common/
		        emacs
		        vi
		        whatever
	  administrivia/
	    users/ --user creation and modification scripts/configs
	    ssh-agent/ --scripts for dealing with passphraseless ssh
	    large-cluster/ --scripts that retrieve and manage hosts across subnets
	    backups/ --backup scripts
	  demos
                  README
		  execnet_demos
		  mpi_demos
		  pvm_demos

	  projects
              project1/
	        README --> all projects should include a readme file
		branches/
		tags/
		trunk/
		      INSTALL
		      /src/main.c
		      /src/header.h
         project2/
	        README
		branches/
		tags/
		trunk/
		      INSTALL
		      /src/blah.c
		      /src/blah.h

