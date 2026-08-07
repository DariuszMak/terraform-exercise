docker run -d `
  --name localstack `
  -p 4566:4566 `
  -p 4510-4559:4510-4559 `
  localstack/localstack:3.8

Write-Host "Waiting for LocalStack S3 to be ready..."
$maxWait = 120
$elapsed = 0
while ($elapsed -lt $maxWait) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:4566/_localstack/health" -Method Get -ErrorAction Stop
        if ($health.services.s3 -eq "available") {
            Write-Host "LocalStack S3 is ready!"
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
    $elapsed += 2
    Write-Host "  ...waiting ($elapsed/$maxWait sec)"
}
if ($elapsed -ge $maxWait) {
    Write-Error "LocalStack S3 failed to initialize within $maxWait seconds."
    exit 1
}

$env:AWS_ACCESS_KEY_ID="test"
$env:AWS_SECRET_ACCESS_KEY="test"
$env:AWS_DEFAULT_REGION="eu-west-1"

terraform init
terraform apply -auto-approve -var="endpoint=http://localhost:4566"

aws --endpoint-url=http://localhost:4566 s3 ls

"Hello from LocalStack S3" | Set-Content test.txt

aws --endpoint-url=http://localhost:4566 s3 cp test.txt s3://terraform-localstack-demo

aws --endpoint-url=http://localhost:4566 s3 ls s3://terraform-localstack-demo

Start-Process "http://localhost:4566/terraform-localstack-demo"
