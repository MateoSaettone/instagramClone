import React, { useState } from 'react'
import Post from './posts/Post'
import Suggestions from './Suggestions'
import "./Timeline.css"

function Timeline() {
    const [posts, setPost] = useState([
      {
        user: "mateosaettone02",
        postImage: "https://media.tenor.com/LjeBWJ0cK1gAAAAM/monkey-sad.gif",
        likes: 120,
        timestamp: "2d",
      },
      {
        user: "henriquegamonal03",
        postImage: "https://creatorset.com/cdn/shop/files/Screenshot_2023-11-09_024317_2048x2048.png?v=1699490717",
        likes: 120,
        timestamp: "12h",
      },
      {
        user: "ethanjoseph02",
        postImage: "https://media.tenor.com/awZg-WgEyTYAAAAM/goofy-funny.gif",
        likes: 120,
        timestamp: "1d",
      },
      {
        user: "nicknechiev04",
        postImage: "https://media.tenor.com/Y7wZjkZx1ksAAAAj/monkey-thinking-meme-monkey-thinking-sticker.gif",
        likes: 120,
        timestamp: "4d",
      },
      {
        user: "anthonyvk05",
        postImage: "https://s.w-x.co//util/image/w/ap_637848761074_0.jpg?crop=16:9&width=480&format=pjpg&auto=webp&quality=60",
        likes: 120,
        timestamp: "2h",
      },
    ]);
  return (
    <div className="timeline">
      <div className="timeline__left">
        <div className="timeline__posts">
          {posts.map(post => (
            <Post 
              user = {post.user} 
              postImage = {post.postImage}
              likes = {post.likes}
              timestamp = {post.timestamp}
            />
          ))}
      </div>
    </div>
    <div className="timeline__right">
          <Suggestions />
       </div>
    </div>
  );
}

export default Timeline