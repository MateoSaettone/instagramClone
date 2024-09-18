import React, { useState, useEffect } from 'react';
import Post from './posts/Post';
import Suggestions from './Suggestions';
import Stories from './stories/Stories'; // Import the Stories component
import './Timeline.css';
import axios from 'axios';

function Timeline() {
	const [posts, setPosts] = useState([]);
	const [stories, setStories] = useState([]); // State for stories
	// const [suggestions, setSuggestions] = useState([]);

	// Fetch posts from FastAPI when the component mounts
	useEffect(() => {
		const fetchPosts = async () => {
			try {
				const response = await axios.get('http://localhost:8000/posts/');
				console.log('Fetched posts:', response.data);
				setPosts(response.data);
			} catch (error) {
				console.error('Error fetching posts:', error);
			}
		};

		fetchPosts();
	}, []);

	// Fetch stories from FastAPI when the component mounts
	useEffect(() => {
		const fetchStories = async () => {
			try {
				const response = await axios.get('http://localhost:8000/stories/');
				console.log('Fetched stories:', response.data);
				setStories(response.data);
			} catch (error) {
				console.error('Error fetching stories:', error);
			}
		};

		fetchStories();
	}, []);

	return (
		<div className="timeline">
			<div className="timeline__left">
				<div className="timeline__stories">
					{/* Stories section */}
					{stories.length > 0 ? (
						<Stories stories={stories.map(story => ({
							user: story.username,
							image: story.image_url, // Map the image from the API's 'url' field
						}))} />
					) : (
						<p>No stories available</p>
					)}
				</div>
				<div className="timeline__posts">
					{posts.length > 0 ? (
						posts.map((post) => (
							<Post
								key={post.id}
								user={post.username || ''} 
								postImage={post.image_url} 
								likes={post.likes} 
								timestamp={post.timestamp || 'Just now'}
								description={post.description || ''} 
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
