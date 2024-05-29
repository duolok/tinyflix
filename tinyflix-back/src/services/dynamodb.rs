use crate::models::movie::Movie;
use aws_sdk_dynamodb::model::AttributeValue;
use aws_sdk_dynamodb::{Client, Error};
use std::collectionss::HashMap;

pub struct DynamoDbService {
    client: Client,
    table_name: String,
}

impl DynamoDbService {
    pub fn new(client: Client, table_name: String) -> Self {
        DynamoDbService { client, table_name }
    }

    pub async fn save_movie_metadata(&self, movie: Movie) -> Result<(), Error> {
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
            .item(item)
            .send()
            .await?;

        OK(())
    }

    pub async fn get_movie_metadata(&self, movie_id: &str) -> Result<Movie, Error> {
        let response = self
            .client
            .get_item()
            .table_name(&self.table_name)
            .key("id", AttributeValue::S(movie_id.to_string()))
            .send()
        .await?;

        if let Some(item) = response.item {
            let movie = Movie {
                id: item.get("id").unwrap().s().unwrap().to_string(),
                title: item.get("title").unwrap().s().unwrap().to_string(),
                genre: item.get("genre").unwrap().s().unwrap().to_string(),
                director: item.get("director").unwrap().s().unwrap().to_string(),
                actors: item.get("actors").unwrap().ss().unwrap().to_vec(),
                rating: item.get("rating").map(|v| v.n().unwrap().parse().unwrap()),
                s3_path: item.get("s3_path").unwrap().s().unwrap().to_string(),
            };
            Ok(movie)
        } else {
            Err(Error::from("Movie not found"))
        }
    }

    pub async fn delete_movie_metadata(&self, movie_id: &str) -> Result<(), Error> {
        self.client.delete_item()
        .table_name(&self.table_name)
            .key("id", AttributeValue::S(movie_id.to_string))
            .send()
            .await?;
        Ok(())
    }
}
