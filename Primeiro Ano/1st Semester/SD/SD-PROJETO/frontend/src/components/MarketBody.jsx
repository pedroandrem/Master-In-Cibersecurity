import { useState } from "react";
import styles from '../styles/MarketBody.module.css';
import Item from './Item';

import { FaAngleDoubleLeft, FaAngleDoubleRight} from "react-icons/fa";


function MarketBody() {
  const [items] = useState([
    { id: 1, title: "Tesla Model 3", briefDescription: 'Hybrid SUV with bold styling', currentPrice: '1000' },
    { id: 2, title: "BMW X5", briefDescription: 'Hyundais unusual-looking family SUV contender', currentPrice: '100' },
    { id: 3, title: "Audi A4", briefDescription: 'Hyundais unusual-looking family SUV contender', currentPrice: '100' },
    { id: 4, title: "Daniel", briefDescription: 'Hybrid SUV with bold styling', currentPrice: '100' },
    { id: 5, title: "Jota", briefDescription: 'Hyundais unusual-looking family SUV contender', currentPrice: '100' },
    { id: 6 ,title: "Pedro", briefDescription: 'Hybrid SUV with bold styling', currentPrice: '100' },
    // 7 { title: "Pedro", briefDescription: 'Hybrid SUV with bold styling', currentPrice: '100' },
  ]);

  const displayedItems = items.slice(0, 6);

  const [page, setPage] = useState(0);
  const itemsPerPage = 3;
  const totalPages = Math.ceil(displayedItems.length / itemsPerPage);

  const handleNext = () => {
    if (page < totalPages - 1) setPage(page + 1);
  };

  const handlePrev = () => {
    if (page > 0) setPage(page - 1);
  };

  const startIndex = page * itemsPerPage;
  const visibleItems = displayedItems.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className={styles['market-container']}>

      <h1 className={styles["search-title"]}> HERE WILL BE A SEACH </h1>
      
      <h1 className={styles['big-deals-title']}>Big Deals</h1>
      <div className={styles['carousel-container']}>
        <button 
          onClick={handlePrev} 
          disabled={page === 0}
          className={styles['arrow-button']}
        >
          <FaAngleDoubleLeft />
        </button>

        <div className={styles['grid']}>
          {visibleItems.map((item, index) => (
            <Item key={startIndex + index} item={item} />
          ))}
        </div>

        <button 
          onClick={handleNext} 
          disabled={page >= totalPages - 1}
          className={styles['arrow-button']}
        >
          <FaAngleDoubleRight />
        </button>
      </div>

      <h1 className={styles['other-offers-title']}>Other Offers</h1>

    </div>
  );
}

export default MarketBody;
