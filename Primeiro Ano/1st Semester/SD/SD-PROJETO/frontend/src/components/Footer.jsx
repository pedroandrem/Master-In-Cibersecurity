import React from 'react'
import styles from '../styles/Footer.module.css'


function Footer({top}) {
  return (
    <div 
      style={{
        top: top
      }}
    className={styles['footer-container']}>


        <div className={styles['footer-title-container']}>
            <a className={styles['title']}>Grupos 7: Auction</a>
        </div>
    </div>
  )
}

export default Footer