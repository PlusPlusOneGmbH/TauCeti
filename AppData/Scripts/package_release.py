 

from subprocess import call

call("uv version --bump patch")
import tomllib
with open("pyproject.toml", "rb") as projecttoml:
    projectdata = tomllib.load( projecttoml )
    version = projectdata["project"]["version"]

search_tag = "package_release_candidate"
release_candidates = parent.Project.findChildren( tags = [search_tag] )


for target in release_candidates:
    # We actually do not do this. We just do some cleanup like running pr-release and removing docked comps.

    #for child in list( target.findChildren( tags = [op("PrivateInvestigator").par.Tag.eval()] ) ) + [target]:
    #    debug(f"Removing tag from {child}")
    #    child.tags.remove( op("PrivateInvestigator").par.Tag.eval() )
    
    for docked_comp in target.docked:
        docked_comp.dock = None

    prereleasescript = target.op("pre_release")
    if prereleasescript is not None: prereleasescript.run()
    op("PrivateInvestigator").Save( target )


for target in release_candidates:
    target.tags.remove(search_tag)
    op("PrivateInvestigator").Release( target )

call("git add .")
call(f'git commit . -m "Version {version}"')



