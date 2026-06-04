.PHONY: redis redis-stop redis-logs

redis:
	docker run -d --name redis -p 6379:6379 redis:7-alpine

redis-stop:
	docker stop redis && docker rm redis

redis-logs:
	docker logs -f redis
