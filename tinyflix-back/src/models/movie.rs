use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Movie {
    pub id: String,
    pub title: String,
    pub genre: String,
    pub director: String,
    pub actors: Vec<String>,
    pub rating: Option<f32>,
    pub s3_path: String,
}

