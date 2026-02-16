import { useNavigate } from 'react-router-dom';

import styles from '../styles/Item.module.css';
import vite from '../../public/vite.svg';


function Item({ item }) {

  const navigate = useNavigate()

  return (
    <div className={styles['item-container']}>
        <h1 className={styles['item-title']}>{item.title}</h1>
        <p className={styles['item-briefDescription']}>
          {item.briefDescription.slice(0, 35)}{item.briefDescription.length > 20 ? ' ...' : ''}
        </p>
        <div className={styles['image-wrapper']}>
          <img 
            className={styles['item-image']}
            src={vite}
            alt='Item image'
          />
        </div>

        <div className={styles['item-price-container']}>
          <button className={styles['learn-more']}>
            <span className={styles['circle']} aria-hidden="true">
              <span className={styles['icon']}> {">"} </span>
            </span>
            <span className={styles['button-text']}>{item.currentPrice}</span>
          </button>


        </div>

    </div>
  );
}

export default Item;
