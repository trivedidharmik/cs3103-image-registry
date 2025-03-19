CREATE TABLE Images (
    imageId INT AUTO_INCREMENT PRIMARY KEY,
    userId INT NOT NULL,
    url VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    uploadedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    isVisible ENUM('public', 'private') DEFAULT 'public',
    FOREIGN KEY (userId) REFERENCES Users(userId) ON DELETE CASCADE
);