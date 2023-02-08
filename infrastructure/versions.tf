terraform {
  required_providers {
    heroku = {
      source = "heroku/heroku"
    }
    herokux = {
      source = "davidji99/herokux"
    }
  }
  cloud {
    organization = "AndreasBlank"

    workspaces {
      name = "Pizza_Bot"
    }
  }
  required_version = ">= 0.13"
}
