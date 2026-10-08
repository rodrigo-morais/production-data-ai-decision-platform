FROM golang:1.23-alpine AS build
WORKDIR /src
COPY go.mod .
COPY *.go .
RUN CGO_ENABLED=0 go test ./... && CGO_ENABLED=0 go build -o /score-api .

FROM build AS test
RUN CGO_ENABLED=0 go test ./...

FROM build AS benchmark
RUN CGO_ENABLED=0 go test -bench=BenchmarkScore -benchmem -count=3 ./...

FROM scratch AS runtime
COPY --from=build /score-api /score-api
EXPOSE 8081
ENTRYPOINT ["/score-api"]
