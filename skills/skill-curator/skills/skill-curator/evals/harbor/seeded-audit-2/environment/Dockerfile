FROM python:3.12-slim

RUN apt-get -o Acquire::Retries=3 update && \
    apt-get -o Acquire::Retries=3 install -y --no-install-recommends bash curl git jq procps ripgrep && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/skills /logs/agent /logs/verifier

# A small Python project with seven installed project skills and planted problems:
# a duplicate pair, a conflicting pair, a skill with no description, and a skill
# whose script does not exist. commit-helper is healthy.
# The fixtures are stored as SKILL.md.fixture so SkillEvaluator's baseline guard
# does not mistake them for skill packages; they are test data, not the skill under test.
COPY seed/ /workspace/project/
RUN find /workspace/project/team-skills -name 'SKILL.md.fixture' -exec sh -c 'mv "$1" "${1%.fixture}"' _ {} \; && \
    printf 'fastapi==0.115.0\npytest==8.3.5\n' > /workspace/project/requirements.txt && \
    find /workspace/project/team-skills -type f -exec sha256sum {} + | sort > /opt/seed-skills.sha256
WORKDIR /workspace/project
