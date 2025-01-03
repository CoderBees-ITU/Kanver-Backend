from database.helper import get_db_with_config

def get_users_that_needs_update(config, batch_size=100):
    """
    Generator function to fetch users in batches that need updates using fetchmany.

    Args:
        config: The database configuration object.
        batch_size: Number of records to fetch in each batch.

    Yields:
        A list of user dictionaries in each batch.
    """
    try:
        connection = get_db_with_config(config)
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT U.*
        FROM `User` U
        LEFT JOIN `Banned_Users` B ON U.TC_ID = B.TC_ID
        WHERE 
            (U.Last_Donation_Date IS NULL OR U.Last_Donation_Date <= DATE_SUB(CURDATE(), INTERVAL 90 DAY))
            AND U.Is_Eligible = FALSE
            AND (B.TC_ID IS NULL OR (B.Unban_Date IS NOT NULL AND B.Unban_Date <= CURDATE()))
        """
        cursor.execute(query)
        while True:
            users = cursor.fetchmany(batch_size)
            if not users:
                break
            yield users
    finally:
        cursor.close()
        connection.close()
        

def update_users_to_set_eligiblity(users, config):
    """
    Task to update eligibility for a batch of users and add email sending task.

    Args:
        users: List of user dictionaries.
        config: The database configuration object.
    """
    try:
        connection = get_db_with_config(config)
        cursor = connection.cursor()

        update_query = """
        UPDATE `User` 
        SET Is_Eligible = TRUE
        WHERE TC_ID IN (%s)
        """
        
        tc_ids = [user['TC_ID'] for user in users]
        if tc_ids:
            formatted_ids = ', '.join(map(str, tc_ids))
            cursor.execute(update_query % formatted_ids)
            connection.commit()
    finally:
        cursor.close()
        connection.close()