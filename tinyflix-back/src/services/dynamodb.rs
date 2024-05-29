use crate::models::movie::Movie;
use aws_sdk_dynamodb::types::AttributeValue;
use aws_sdk_dynamodb::{Client, Error as DynamoDbError};
use std::collections::HashMap;

pub struct DynamoDbService {
    client: Client,
    table_name: String,
}

impl DynamoDbService {
    pub fn new(client: Client, table_name: String) -> Self {
        DynamoDbService { client, table_name }
    }

    pub async fn save_movie_metadata(&self, movie: Movie) -> Result<(), DynamoDbError> {
        let mut item = HashMap::new();
        item.insert("id".to_string(), AttributeValue::S(movie.id.clone()));
        item.insert("title".to_string(), AttributeValue::S(movie.title.clone()));
        item.insert("genre".to_string(), AttributeValue::S(movie.genre.clone()));
        item.insert("director".to_string(), AttributeValue::S(movie.director.clone()));
        item.insert("actors".to_string(), AttributeValue::Ss(movie.actors.clone()));
        item.insert("rating".to_string(), AttributeValue::N(movie.rating.unwrap_or(0.0).to_string()));
        item.insert("s3_path".to_string(), AttributeValue::S(movie.s3_path.clone()));

        self.client
            .put_item()
            .table_name(&self.table_name)
            .set_item(Some(item))
            .send()
            .await?;

        Ok(())
    }

    pub async fn get_movie(&self, movie_id: &str) -> Result<Movie, DynamoDbError> {
        let response = self
            .client
            .get_item()
            .table_name(&self.table_name)
            .key("id", AttributeValue::S(movie_id.to_string()))
            .send()
        .await?;

        if let Some(item) = response.item {
            let movie = Movie {
                id: item.get("id").and_then(|v| v.as_s().ok()).unwrap().to_string(),
                title: item.get("title").and_then(|v| v.as_s().ok()).unwrap().to_string(),
                genre: item.get("genre").and_then(|v| v.as_s().ok()).unwrap().to_string(),
                director: item.get("director").and_then(|v| v.as_s().ok()).unwrap().to_string(),
                actors: item
                    .get("actors")
                    .and_then(|v| v.as_ss().ok())
                    .unwrap()
                    .to_vec(),
                rating: item
                    .get("rating")
                    .and_then(|v| v.as_n().ok())
                    .and_then(|n| n.parse().ok()),
                s3_path: item.get("s3_path").and_then(|v| v.as_s().ok()).unwrap().to_string(),
            };
            Ok(movie)
        } else {
            unimplemented!()
        }
    }

    pub async fn delete_movie(&self, movie_id: &str) -> Result<(), DynamoDbError> {
        self.client
            .delete_item()
            .table_name(&self.table_name)
            .key("id", AttributeValue::S(movie_id.to_string()))
            .send()
        .await?;
        Ok(())
    }
}
