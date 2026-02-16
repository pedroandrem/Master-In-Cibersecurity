import ItemBody from "../components/ItemBody";
import NavBar from "../components/NavBar";

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
        <ItemBody/>
    </>
    );
};
  
export default MarketPage;
  
