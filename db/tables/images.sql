CREATE TABLE Images (
    imageId INT AUTO_INCREMENT PRIMARY KEY,
    userId INT NOT NULL,
    fileName VARCHAR(255) NOT NULL, -- (e.g., "1234.jpg")
    fileExtension VARCHAR(10) NOT NULL, -- (e.g., "jpg", "png")
    title VARCHAR(255),
    description TEXT,
    uploadedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    isVisible ENUM('public', 'private') DEFAULT 'public',
    FOREIGN KEY (userId) REFERENCES Users(userId) ON DELETE CASCADE
);