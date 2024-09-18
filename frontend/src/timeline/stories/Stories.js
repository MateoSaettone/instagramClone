import React, { useState, useRef } from 'react';
import './Stories.css';
import { Avatar } from '@mui/material';

function Stories({ stories }) {
	const [activeStory, setActiveStory] = useState(null);
	const storiesRef = useRef(null); // Ref for the stories container

	const handleStoryClick = (story) => {
		setActiveStory(story);
	};
	
	const scrollLeft = () => {
		storiesRef.current.scrollBy({
			left: -300, 
			behavior: 'smooth'
		});
	};

	const scrollRight = () => {
		storiesRef.current.scrollBy({
			left: 300, 
			behavior: 'smooth'
		});
	};

	const closeStoryViewer = () => {
		setActiveStory(null);
	};

	return (
		<div className="stories-wrapper">
			<button className="scroll-button left" onClick={scrollLeft}>
				←
			</button>

			<div className="stories" ref={storiesRef}>
				<div className="stories__list">
					{stories.map((story, index) => (
						<div
							key={index}
							className="story"
							onClick={() => handleStoryClick(story)}
						>
							<div className="story__border">
                                <img src={story.image} alt={story.user} className="story__avatar" />
							</div>
							<span className="story__username">{story.user || 'Unknown'}</span>
						</div>
					))}
				</div>
			</div>

			<button className="scroll-button right" onClick={scrollRight}>
				→
			</button>

			{activeStory && (
				<div className="story__viewerOverlay" onClick={closeStoryViewer}>
					<div className="story__viewer" onClick={(e) => e.stopPropagation()}>
						<img
							src={activeStory.image}
							alt={activeStory.user}
							className="story__image"
						/>
						<span className="story__viewerUser">{activeStory.user || 'Unknown'}</span>
						<span className="story__viewerClose" onClick={closeStoryViewer}>
							Close
						</span>
					</div>
				</div>
			)}
		</div>
	);
}

export default Stories;
