import { NavLink } from 'react-router-dom'
import styles from '../styles/NavBar.module.css'

function NavBar({ links }) {
  return (
    <nav className={styles['navbar-container']}>
      <div className={styles['logo-container']}>
        <NavLink to="/">Auction</NavLink>
      </div>

      <ul className={styles['nav-links-container']}>
        {links.map((link, index) => (
          <li key={index}>
            <NavLink
              to={link.href}
              className={({ isActive }) =>
                isActive ? `${styles[link.className]} ${styles.active}` : styles[link.className]
              }
            >
              {link.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}

export default NavBar