import NotificationBody from "../components/NotificationBody";
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";

const MarketPage = () => {

  const navLinks = [
    { label: 'Market', href: '/market', className: 'market-anchor' },
    { label: 'Item', href: '/item', className: 'item-anchor'},
    { label: 'Notifications', href: '/notification', className: 'notifications-anchor'}
  ];

  const limitedLinks = navLinks.slice(0,4)

  return (
    <>
        <NavBar links={limitedLinks} />
        <NotificationBody/>
        <Footer />
    </>
    );
};
  
export default MarketPage;
  
