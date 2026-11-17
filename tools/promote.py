"""Move machine translations into the main file, for review, or clear the ones already approved there.

    python tools/promote.py spa 1002470 1358280 ...    move these entries from spa_machine.json into spa.json, as
                                                       pending: the reviewer edits and approves (or rejects) them there
    python tools/promote.py spa --approved             remove from spa_machine.json the entries spa.json has approved

An entry spa.json already has is left where it is (its translation there comes first)."""
import json
import sys

from check import DATA, dump


def load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"format": 1, "entries": {}}


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    code, ids = argv[0], argv[1:]
    main_path, machine_path = DATA / f"{code}.json", DATA / f"{code}_machine.json"
    main, machine = load(main_path), load(machine_path)
    if ids == ["--approved"]:
        done = [eid for eid in machine["entries"] if main["entries"].get(eid, {}).get("status") == "approved"]
        for eid in done:
            del machine["entries"][eid]
        print(f"removed {len(done)} machine translations approved in {main_path.name}")
    else:
        for eid in ids:
            if eid in main["entries"]:
                print(f"{eid}: already in {main_path.name}, left as it is")
            elif eid not in machine["entries"]:
                print(f"{eid}: not in {machine_path.name}")
            else:
                main["entries"][eid] = machine["entries"].pop(eid)
                print(f"{eid}: moved to {main_path.name} (pending)")
        main_path.write_text(dump(main), encoding="utf-8", newline="\n")
    machine_path.write_text(dump(machine), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
