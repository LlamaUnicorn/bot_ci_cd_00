cd /home/dave/PycharmProjects/bot_ci_cd_00 || exit
git pull origin main
docker-compose -f /home/dave/PycharmProjects/bot_ci_cd_00/docker-compose.yml down --remove-orphans
docker-compose -f /home/dave/PycharmProjects/bot_ci_cd_00/docker-compose.yml up -d

