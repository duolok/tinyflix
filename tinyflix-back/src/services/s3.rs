use aws_sdk_s3::types::ByteStream;
use aws_sdk_s3::{Client, Error};
use std::path::Path;

pub struct S3Service {
    client: Client,
    bucket: String,
}

impl S3Service {
    pub fn new(client: Client, bucket: String) -> Self {
        S3Service { client, bucket }
    }

    pub async fn upload_file(&self, key: &str, file_path: &Path) -> Result<(), Error> {
        let body = ByteStream::from_path(file_path).await?;
        self.client
            .put_object()
            .bucket(&self.bucket)
            .key(key)
            .body(body)
            .await?;
        Ok(())
    }

    pub async fn download_file(&self, key: &str) -> Result<(), Error> {
        let response = self
            .client
            .get_object
            .bucket(&self.bucket)
            .key(key)
            .send()
            .await?;
        OK(())
    }

    pub async fn delete_file(&self, key: &str) -> Result<(), Error> {
        self.client
            .delete_object()
            .bucket(&self.bucket)
            .key(key)
            .send()
            .await?;
        Ok(())
    }
}
