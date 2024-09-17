import React from 'react';
import './Post.css';
import { Avatar } from '@mui/material';
import {
	BookmarkBorder,
	ChatBubbleOutline,
	FavoriteBorder,
	MoreHoriz,
	Telegram,
} from '@mui/icons-material';

function Post({ user, postImage, likes, timestamp, description }) {
	return (
		<div className="post">
			<div className="post__header">
				<div className="post__headerAuthor">
					<Avatar>{user.charAt(0).toUpperCase()}</Avatar>
					<span className="post__username"> {user} </span>
					<span className="post__dot"> • </span>
					<span className="post__timestamp"> {timestamp} </span>
				</div>
				<MoreHoriz />
			</div>
			<div className="post__image">
				<img
					src={postImage}
					alt="postImage"
				/>
			</div>

			<div className="post__footer">
				<div className="post__footerIcons">
					<div className="post__iconsMain">
						<FavoriteBorder className="post__like" />
						<ChatBubbleOutline className="post__comment" />
						<Telegram className="post__send" />
					</div>
					<div className="post__save">
						<BookmarkBorder className="postIcon" />
					</div>
					<div className="post__iconsMain"></div>
				</div>
				<span className="post__likes"> {likes} likes </span>
			</div>
			<div className="post__description">
				<span className="post__descriptionUsername"> {user} </span>
				<span className="post_descriptionText"> {description} </span>
			</div>
		</div>
	);
}

export default Post;
