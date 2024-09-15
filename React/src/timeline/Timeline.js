import React, { useState, useEffect } from 'react';
import Post from './posts/Post';
import Suggestions from './Suggestions';
import './Timeline.css';
// If using axios, import it
import axios from 'axios';

function Timeline() {
	const [posts, setPosts] = useState([]);

	// Fetch posts from FastAPI when the component mounts
	useEffect(() => {
		const fetchPosts = async () => {
		  try {
			const response = await axios.get('http://localhost:8000/posts/');
			console.log('Fetched posts:', response.data);  // Add this log
			setPosts(response.data); 
		  } catch (error) {
			console.error('Error fetching posts:', error);  // Add this log
		  }
		};
	  
		fetchPosts();
	  }, []);	  

	return (
		<div className="timeline">
			<div className="timeline__left">
				<div className="timeline__posts">
					{posts.length > 0 ? (
						posts.map((post) => (
							<Post
								key={post.id}
								user={`User ${post.user_id}`}  // Mapping user_id to a placeholder user name (you can fetch user data separately if needed)
								postImage={post.image_url}      // Mapping image_url to postImage
								likes={post.likes}              // No change needed for likes
								timestamp={post.timestamp || "Just now"}  // Since timestamp doesn't exist, using a placeholder
							/>
						))
					) : (
						<p>No posts available</p>
					)}
				</div>
			</div>
			<div className="timeline__right">
				<Suggestions />
			</div>
		</div>
	);
}

export default Timeline;
