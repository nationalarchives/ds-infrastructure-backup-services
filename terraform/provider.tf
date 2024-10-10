# provider klayers is needed for lambda functions allowing to use layers more
# information can be found here: https://github.com/keithrozario/Klayers
#

terraform {
    required_version = ">= 1.6.3"

    # TODO Consider if this is the correct provider version
    required_providers {
        aws          = ">= 5.2.9"
        klayers = {
            version = "~> 1.0.0"
            source  = "ldcorentin/klayer"
        }
    }
}
