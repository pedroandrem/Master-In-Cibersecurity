import { useState, useEffect } from "react";
import styles from '../styles/NotificationBody.module.css';
import socket from "../socket";

function NotificationBody() {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const handleListed = (data) => {
      setMessages((prev) => [
        {
          type: "announcement",
          tags: ["announcement", "listing"],
          message: `New item listed: ${data.name} — ${data.description}. Minimum bid: $${data.minimum_bid}, Highest bid: $${data.highest_bid}, Closing: ${data.closing_date}`
        },
        ...prev
      ]);
    };

    const handleBided = (data) => {
      setMessages((prev) => [
        {
          type: "announcement",
          tags: ["announcement", "biding"],
          message: data.message || "Someone bided!"
        },
        ...prev
      ]);
    };

    socket.on("someone_listed", handleListed);
    socket.on("someone_bided", handleBided);

    return () => {
      socket.off("someone_listed", handleListed);
      socket.off("someone_bided", handleBided);
    };
  }, []);

  return (
    <div className={styles['notification-container']}>
      {messages.length === 0 ? (
        <p>No notifications yet</p>
      ) : (
        messages.map((msg, index) => (
          <div key={index} className={`${styles.notificationItem} ${styles[msg.type]}`}>
            <strong>{msg.type.toUpperCase()}</strong>
            <p>{msg.message}</p>

            <div className={styles.tags}>
              {msg.tags.map((tag, i) => (
                <span key={i} className={styles.tag}>{tag}</span>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default NotificationBody;
