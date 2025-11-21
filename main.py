#!/usr/bin/env python3

import glob
import os

from fleet.query.client import ManagementApiClient
from fleet.query.utils import load_script_args, delete_all, config_parser_init, load_map_config
from fleet.query.api import run_queries, get_tenant_cookie
from fleet.models import TenantName, CarName


def main() -> None:
    args = load_script_args()
    config = config_parser_init(args.config)
    config.read(args.config)
    api_client = ManagementApiClient(
        host=config["DEFAULT"]["Url"],
        api_key={"APIKeyAuth": config["DEFAULT"]["ApiKey"]},
        test=args.test,
    )
    args.maps = os.path.join(args.maps, "")
    already_added_cars: dict[TenantName, list[CarName]] = {}
    already_deleted_tenants: list[str] = []
    for map_file_path in glob.iglob(f"{args.maps}*"):
        print(f"\nProcessing file: {map_file_path}")
        try:
            map_config = load_map_config(map_file_path)
        except Exception as exception:
            print(f"Error reading map file '{map_file_path}': {exception}")
            return
        try:
            tenant_name: str = map_config.tenant
            print(f"Using tenant: {tenant_name}")
            tenant_cookie = get_tenant_cookie(api_client, tenant_name)
            if not tenant_cookie:
                print(
                    f"Tenant '{tenant_name}' does not exist and could not be created. "
                    f"Cannot create entities for map '{map_file_path}'"
                )
                return
            api_client.set_default_header("Cookie", tenant_cookie)
            if args.delete and tenant_name not in already_deleted_tenants:
                delete_all(api_client)
                already_deleted_tenants.append(tenant_name)
                print(f"Entries for tenant {tenant_name} deleted")

            if tenant_name not in already_added_cars:
                already_added_cars[tenant_name] = []
            run_queries(api_client, map_config, already_added_cars[map_config.tenant])

        except Exception as exception:
            print(f"Error processing map file '{map_file_path}': {exception}")
            return

    print("\nFleet management updated")


if __name__ == "__main__":
    main()
