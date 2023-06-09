import applicationsConstants as ApplicationsConstants
import applicationsMapConstants as ApplicationsMapConstants

class CarrierData():
    """ class to store the carrier related information """

    def __init__(self, carrierName, region, orgs, useEnabledSM):
        """
        Constructor for CarrierData.

        Parameters
        ----------
        carrierName: str
            Name of the carrier.
        region: str
            Region of the carrier.
        orgs: str
            Space separated org for the carrier.
        useEnabledSM: boolean
            Set it as TRUE if only enabled shipmethod needed else FALSE.
        """
        self.carrier = carrierName.strip().upper()
        self.region = self.setRegion(region)
        self.orgs = self.setOrg(orgs, region)
        self.useEnabledSM = useEnabledSM

    def setRegion(self, region):
        """
        Method use to set the basic carrier region for which analysis is going to happen.
        Method checks if region code is supported or not in our system.

        Parameters
        ----------
        region: str
            Region of the carrier.

        Returns
        -------
        str
            Region code in upper case.

        Raises
        ------
        ValueError
            If region is not yet supported it will throw value error.
        """
        regionCode = region.strip().upper()
        if regionCode not in ApplicationsMapConstants.REGION_SUPPORTED:
            error_messsage = f"Only {', '.join(ApplicationsMapConstants.REGION_SUPPORTED)} regions are supported for now"
            raise ValueError(error_messsage)
        return regionCode

    def setOrg(self, orgs, region):
        """
        Method use to set org list for the carrier for which analysis is going to happen.
        If user did not put any org, it will use default org list for given region.

        Parameters
        ----------
        orgs: str
            Space separated org for the carrier.
        region: str
            Region of the carrier.

        Returns
        -------
        list
            Org list in upper case.
        """
        region = region.strip().upper()
        orgs = orgs.strip()
        if orgs == ApplicationsConstants.EMPTY_STRING:
            return ApplicationsMapConstants.ORGS[region]
        orgList = orgs.split(ApplicationsConstants.SPACE)
        return [org.upper().strip() for org in orgList if org.upper().strip() != ApplicationsConstants.EMPTY_STRING]
