from diot import Diot
from pyppl import Proc

pProcess1 = Proc(
	config = Diot(annotate = """
		@requires:
			[tool1]
			install = "ls"
			validate = "false"
		""")
)

pProcessNoAnno = Proc()

pProcessNoValid = Proc(
	config = Diot(annotate = """
		@requires:
			[tool1]
			install = "ls"
		""")
)

pProcessNoInstall = Proc(
	config = Diot(annotate = """
		@requires:
			[tool1]
			validate = "false"
		""")
)

pProcessWhen = Proc(
	config = Diot(annotate = """
		@requires:
			[tool2]
			install = "ls"
			validate = "false"
			when = "false"
		""")
)

pProcessPass = Proc(
	config = Diot(annotate = """
		@requires:
			[tool2]
			install = "ls"
			validate = "true"
		""")
)

pProcessInstallFail = Proc(
	config = Diot(annotate = """
		@requires:
			[tool2]
			install = "false"
			validate = "false"
		""")
)
